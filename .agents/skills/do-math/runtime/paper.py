"""Write the paper of an instance whose root is settled by a formal proof.

    python paper.py <instance> --out <folder> [--resume] [--parallel <n>] [--dry-run]
                    [--model <provider/model>] [--effort <effort>] [--typeset-only]
                    [--draft | --from-draft <folder>] [--title-page <file>] [--main <declaration>]
                    [--open-findings [<numbers>]] [--tex <command...>]

One command produces the paper to the end without stopping for the user. What the sessions it
launches do not decide is fixed in ../reference/paper-method.md, which they receive. For the person
who runs the command, ../reference/operations.md describes it in the section "The paper". The
stages, each with the place in this file that says what it does:

  materials    extract, load_collection
  plan         Paper.make_plan, check_plan
  write        Paper.write_parts, render_brief
  settle       Paper.settle; tight_displays for the second typesetting, in typeset/displays
  reading      Paper.read_and_repair
  likeness     Paper.read_beside_papers
  rereading    Paper.read_again
  comparison   Paper.compare
  resolve      Paper.resolve
  coverage     Paper.cover
  placement    Paper.place

Every loop is bounded by the constants below. Paper.repair says how a repair is divided among
sessions, and Sessions, in command_sessions.py, how a session is launched and its output read.
Sessions.session says what follows when a safeguard of the AI system stopped a session, and
<out>/not-done.json keeps the checks that were not made for that reason.

A repair may rewrite, and a rewriting can lose a step of a proof, so the text that a repair leaves
is read. After every reading but the last of its stage, the next reading does that. The repair
after the last reading is followed by no reading of the whole manuscript, so it is made narrowly,
and a session reads what it changed. Paper.narrow_run gives the steps of such a repair (repair,
settle, read, undo), what holds of the manuscript when they are done, and why a finding can stay
open after them.

<out> receives paper.tex, references.bib, paper.pdf, plan.json, correspondence.json (which element
each numbered statement states; never inside the paper), materials.md and log.json (what was
launched and what each check found). The work stays beside them: materials.json, study.md (the
planning session's account of how the chosen papers are written), parts/ (the abstract and the
sections as they stand), state.json, sessions/ and typeset/, narrow/ while a narrow repair is under
way (the parts as they were read, and the texts that are put back), and resolve/ while the stage
`resolve` is under way (the plan and the parts that its session returned). --typeset-only does not
use the collection.

--draft makes the draft of a paper and no paper (Paper.draft). --from-draft <folder> writes the
paper from a draft (read_draft, extract, carried_plan, Paper.plan_from_draft).

--main <declaration> names the theorem that the paper is built around when that is not the
declaration that settles the root (chosen_main, extract, produce). --title-page <file> names the
authors of the title page and can give the codes of the subject classification (read_title_page,
read_classification, author_lines, assemble).

--resume with the same --out continues a run that was stopped, from what <out> holds: Paper.take_up
reads it, Paper.after_writing says how the stages after the writing go on, and Paper.narrow_run and
Paper.resolve say it for a run that was stopped inside one of them.

--open-findings takes up a run that came to its end with findings left open (act_on_open,
Paper.act). --parallel bounds the sessions that run side by side (Sessions.side_by_side), and
--dry-run launches no session and prints what the run would do next (Paper.preview).

--tex takes the rest of the command line, so it comes last. The name of tectonic, latexmk or pdflatex
by itself is run in the way that program needs. Any other command, also one of the three with options
of its own, is run once in the folder of the manuscript with `paper.tex` appended; it has to leave
paper.pdf with the references and the bibliography resolved, which the script does not check. Without
--tex the first of the three found on PATH is used. When there is none, everything except the
typesetting is done and the command says so; --typeset-only later typesets the manuscript that <out>
already holds.

Exit codes: 0 the paper is complete, or with --draft the draft is; 1 refused or failed; 2 produced
with findings left open (the last `end` event of log.json names them under "open"): a numbered
statement that differs from its element or whose present text was not compared, a sentence of
running text that no element covers, a line wider than the text block, a machine check or a
typesetting that failed; 3 the manuscript is complete and no TeX command was available. What the
readings found and the resolving session or the last narrow repair answered with a reason is under
"kept" in that event and does not make the exit code 2.
"""
import argparse
from contextlib import contextmanager, nullcontext
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from canon import BIB_ENTRY, Canon, declaration_text, read_question_account, read_record, sha256_text
from cli_adapter import build_command, provider_for_model
from command_sessions import PARALLEL, Sessions, Stop, Unusable, alone, collapsed, is_text, read_file
import depmap
from knowledge import ROOT_QUESTION, STANDINGS, replay, root_settlement
from runtime_support import contain_session_processes, popen_options, read_json, write_json, write_text

REFERENCE = Path(__file__).resolve().parents[1] / 'reference'
METHOD = REFERENCE / 'paper-method.md'
PREFERENCES = REFERENCE / 'user-writing-preferences.md'
READER_SECTION = 'The reader'  # the part of the method that the reading session receives, and nothing else of it
# The part of the method that a reading beside real papers receives, and nothing else of it.
LIKENESS_SECTION = 'Reading the manuscript beside real papers'
# The first of the last two sections of the method, which say what the script gives each session and what is checked
# after the writing. No session receives the two: one that is given the method whole has it up to this heading.
GIVEN_SECTION = 'What each session works from'
EXEMPLARS = Path(__file__).resolve().parents[1] / 'exemplars'  # the collection: manifest.json, <key>.tex, fetch.py
MANIFEST_FIELDS = ('key', 'arxiv', 'title', 'authors', 'journal', 'year', 'category', 'field', 'pages', 'licence',
                   'abstract', 'sha256', 'why')

PLAN_ATTEMPTS = 3      # planning sessions before the command gives up on a plan it can carry out
REPAIR_ROUNDS = 3      # repair sessions for one round of machine checks and typesetting
READING_ROUNDS = 3     # independent readings at one time; the repair after the last one is narrow (narrow_run)
CHOSEN_PAPERS = 6      # papers of the collection the plan chooses for the paper to be written like
SECTION_PAPERS = 2     # of those, the papers the plan names for one section; its writer reads them whole
LIKENESS_PAPERS = 4   # papers the plan did not choose, given to one reading beside real papers
LIKENESS_ROUNDS = 8    # readings beside real papers at the most
LIKENESS_CLEAN = 2     # readings in succession without a departure that end those readings
COMPARISON_ROUNDS = 2  # comparisons of the statements; a repair follows every one but the last
TEX_SECONDS = 600      # one TeX command
FETCH_SECONDS = 3600   # one run of the collection's fetch.py
WIDE_PT = 5.0          # a line this many points wider than the text block is sent back to be broken
WIDE = 'lines wider than the text block'
UNCOMPARED = 'numbered statements whose present text was not compared with their elements'
READING = 'reading of the manuscript by itself'
LIKENESS = 'reading of the manuscript beside real papers'
COMPARISON = 'comparison of the numbered statements with their elements'
COVERAGE = 'comparison of the running text with the elements'
MACHINE = 'machine checks of the manuscript'
TYPESETTING = 'typesetting'
# The checks whose findings a repair session can take up one by one, each with the kind of repair that does. The last
# repair that a reading receives, the repair of what the comparison of the running text found, and every repair of
# findings that a finished run left open, is a narrow one: it changes the passages its findings name, and a session
# then reads the passages it changed (Paper.narrow_run).
NARROW_KINDS = {READING: 'reading', LIKENESS: 'likeness', COMPARISON: 'comparison', COVERAGE: 'coverage'}
# The checks whose findings the stage `resolve` closes: each is answered by a change or by a reason, and one that is
# answered by a reason is listed under "kept" at the end of the run and is not open.
READINGS = (READING, LIKENESS)
# Why a finding is open after the last repair it received, as the open list says it under "open_because".
KEPT = 'the repair session kept the text: '
UNDONE = 'changed, and the change was undone, because the reading of the changed passages found it unsound: '
UNANSWERED = 'changed, and the reading of the changed passages found that the change does not answer the finding; the change stays: '
FAILING = ('changed, and every change of this repair was undone, because the manuscript did not pass its machine checks '
           'or could not be typeset with them: ')
NO_CHANGE = 'the repair session reported a change, and the manuscript does not differ from the text that was read'
ONCE_CONFIRMED = ('repaired after the reading that reported it; the one reading that followed found no departure, and '
                  'the readings ended at their bound before a second reading confirmed that')
NOT_CONFIRMED = ('repaired after the reading that reported it; the readings ended at their bound before a reading '
                 'confirmed the repair, because the reading that was to follow was not made')
DIFFERS_NOW = ('the statement was changed by a repair of open findings, and the comparison that followed found this '
               'difference')
DIFFERS_LATE = ('the statement was changed after the comparisons of the statements had ended, and the one comparison '
                'of its present text found this difference; no repair follows that comparison')
COVERED_AGAIN = ('reported when the running text of the section was compared with the elements again, after the repair '
                 'of what the first comparison had reported; no repair follows that comparison')
CLOSING_ATTEMPTS = 3   # sessions that restate statements or take passages out, before the run gives up (Paper.close)
# The stages after the writing whose completion state.json records, in their order; each is a method of Paper.
STAGES = (('reading', 'read_and_repair'), ('likeness', 'read_beside_papers'), ('rereading', 'read_again'),
          ('comparison', 'compare'), ('resolve', 'resolve'), ('coverage', 'cover'), ('placement', 'place'))

ENGINES = ('tectonic', 'latexmk', 'pdflatex')
NUMBERED = ('theorem', 'proposition', 'lemma', 'corollary', 'definition')
ENVIRONMENT = re.compile(r'\\begin\{(' + '|'.join(NUMBERED) + r')\}(.*?)\\end\{\1\}', re.S)
PROOF_ENVIRONMENT = re.compile(r'\\begin\{proof\}.*?\\end\{proof\}', re.S)
# A displayed formula that can carry a label: the environments of amsmath that number their lines.
DISPLAY = re.compile(r'\\begin\{(equation|align|multline|gather|alignat|flalign|eqnarray)\}.*?\\end\{\1\}', re.S)
# The words by which a text names the proof assistant and its library, as whole words with these capitals; a
# letter on either side makes another word ("Leaning"), and a digit does not ("Lean4").
LEAN_WORDS = re.compile(r'(?<![A-Za-z])(?:Lean|Mathlib)(?![A-Za-z])')
FORBIDDEN = re.compile(r'\\(documentclass|usepackage|newcommand|renewcommand|providecommand|def|newtheorem|section|'
                       r'bibliography|bibliographystyle|maketitle|title|author|input|include|setcounter|numberwithin|'
                       r'newenvironment|renewenvironment|DeclareMathOperator|let)\b')
CITE = re.compile(r'\\cite(?:\[[^\]]*\])?\{([^}]*)\}')
REF = re.compile(r'\\(?:eq|page)?ref\{([^}]*)\}')
LABEL = re.compile(r'\\label\{([^}]*)\}')
SECTION_ID = re.compile(r'[a-z][a-z0-9-]*')
from package import MSC as MSC_CODE  # a code of the MSC 2020, such as 05A15; the pipeline holds its selection to the same form
from package import said as shortened  # a text on one line, cut at a word where it is longer than the length given
LABEL_FORM = re.compile(r'[a-z]+:[a-z0-9-]+')
OVERFULL = re.compile(r'Overfull \\hbox \(([0-9.]+)pt too wide\) '
                      r'(?:detected at line (\d+)|in (?:paragraph|alignment) at lines (\d+)--(\d+))')
# What TeX and BibTeX write when a file of the TeX installation is missing: the class, a package or the bibliography
# style of the preamble that the script supplies. No part can be the cause, since the machine checks keep
# \documentclass, \usepackage, \input, \include and \bibliographystyle out of the parts (FORBIDDEN).
MISSING_FILE = re.compile(r"LaTeX Error: File `[^']*' not found|I couldn't open style file \S+")

PREAMBLE = r'''\documentclass{amsart}
\usepackage{amssymb}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}
\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
\theoremstyle{remark}
\newtheorem*{remark}{Remark}
\numberwithin{equation}{section}
\makeatletter
\def\subsection{\@startsection{subsection}{2}\z@{.5\linespacing\@plus.7\linespacing}{-.5em}{\normalfont\bfseries\boldmath}}
\makeatother
'''
# The definition of \subsection is that of amsart with \boldmath added: the heading of a subsection is bold, and
# a formula in it is then bold as well, where the class alone leaves the formula in the weight of the text.
# amsart centres the running head in the line that carries the page number at its outer end, and does not shorten
# it. A head wider than this share of the line would be printed over the page number and out into the margin, so
# such a head is left out and the line carries the page number alone.
RUNNING_HEAD = (r'\sbox0{\normalfont\scriptsize\RunningHead}\ifdim\wd0>.85\textwidth\markboth{}{}'
                r'\else\markboth{\RunningHead}{\RunningHead}\fi')


def not_done_lines(entries):
    """The checks that a run records as not done (Sessions.session), one sentence for each, as a report gives them."""
    return [f"Not made: {entry['what']}. A safeguard of the AI system stopped the session that had this task, in each "
            f"of its {entry['attempts']} attempts." for entry in entries]


def method_part(title):
    """One section of the method document, by its heading."""
    match = re.search(r'^## ' + re.escape(title) + r'\n(.*?)(?=^## |\Z)', read_file(METHOD), re.M | re.S)
    if not match:
        raise Stop(f'{METHOD} has no section "{title}"')
    return match[1].strip()


def method_before_checks():
    """The method document without its last two sections, for every session that is given more of it than single sections."""
    text = read_file(METHOD)
    match = re.search(r'^## ' + re.escape(GIVEN_SECTION) + r'\n', text, re.M)
    if not match:
        raise Stop(f'{METHOD} has no section "{GIVEN_SECTION}"')
    return text[:match.start()]


# ----------------------------------------------------------------------------- the collection of real papers

KEY_FORM = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.+-]*')


def collection_state():
    """The manifest of the collection and the keys whose .tex is missing or differs from its SHA-256."""
    path = EXEMPLARS / 'manifest.json'
    if not path.is_file():
        raise Stop(f'the collection of papers has no manifest: {path} is missing')
    try:
        manifest = json.loads(read_file(path))
    except ValueError as exc:
        raise Stop(f'{path} is not JSON: {exc}')
    if not isinstance(manifest, list) or not all(isinstance(entry, dict) for entry in manifest):
        raise Stop(f'{path} holds an array of objects, one for each paper')
    for number, entry in enumerate(manifest, 1):
        lacking = [field for field in MANIFEST_FIELDS if field not in entry]
        if lacking:
            raise Stop(f'{path}: paper {number} lacks ' + ', '.join(lacking))
        if not (isinstance(entry['key'], str) and KEY_FORM.fullmatch(entry['key'])):
            raise Stop(f"{path}: paper {number} has the key {entry['key']!r}, which cannot name a file")
    keys = [entry['key'] for entry in manifest]
    if len(set(keys)) != len(keys):
        raise Stop(f'{path}: two papers have the same key')
    if len(keys) < CHOSEN_PAPERS + LIKENESS_PAPERS:
        raise Stop(f'{path} lists {len(keys)} papers; the plan chooses {CHOSEN_PAPERS} and each reading beside real '
                   f'papers needs {LIKENESS_PAPERS} others, so the collection has at least '
                   f'{CHOSEN_PAPERS + LIKENESS_PAPERS}')
    wrong = [entry['key'] for entry in manifest
             if not (EXEMPLARS / (entry['key'] + '.tex')).is_file()
             or hashlib.sha256((EXEMPLARS / (entry['key'] + '.tex')).read_bytes()).hexdigest() != entry['sha256']]
    return manifest, wrong


def load_collection():
    """The manifest, the papers by key, and whether fetch.py had to be run; stops when papers stay wrong.

    A paper that is missing or differs from the manifest is fetched by the collection's own script,
    which is run once for all of them with the interpreter that runs this command."""
    manifest, wrong = collection_state()
    fetched = None
    if wrong:
        fetch = EXEMPLARS / 'fetch.py'
        if not fetch.is_file():
            raise Stop(f'papers of the collection are missing or differ from {EXEMPLARS / "manifest.json"}: '
                       + ', '.join(wrong) + f'; and {fetch}, which fetches them, is missing')
        try:
            # -X utf8: fetch.py then prints in UTF-8 whatever the locale, and its output is read as UTF-8 below.
            done = subprocess.run([sys.executable, '-X', 'utf8', str(fetch)], cwd=EXEMPLARS, stdin=subprocess.DEVNULL,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=FETCH_SECONDS,
                                  **popen_options())
            output = done.stdout.decode('utf-8', errors='replace').replace('\r\n', '\n')
            fetched = {'missing_or_different': wrong, 'exit_code': done.returncode, 'output': output[-4000:]}
        except subprocess.TimeoutExpired:
            fetched = {'missing_or_different': wrong, 'exit_code': None,
                       'output': f'fetch.py did not finish within {FETCH_SECONDS} seconds'}
        except OSError as exc:
            raise Stop(f'{fetch} could not be started: {exc}')
        manifest, wrong = collection_state()
        if wrong:
            last = '\n'.join(fetched['output'].strip().splitlines()[-10:])
            raise Stop(f'papers of the collection are missing or differ from {EXEMPLARS / "manifest.json"} after '
                       f'fetch.py ran (exit code {fetched["exit_code"]}): ' + ', '.join(wrong)
                       + f'. Fetch them with: "{sys.executable}" "{fetch}" ' + ' '.join('--only ' + k for k in wrong)
                       + ('\nThe last lines of fetch.py:\n' + last if last else ''))
    papers = {entry['key']: read_file(EXEMPLARS / (entry['key'] + '.tex')) for entry in manifest}
    return manifest, papers, fetched


def unfetched_collection():
    """The manifest, the papers by key and the keys that are missing or differ, for a dry run: nothing is fetched.

    A run fetches such a paper over the network; here it is an empty text."""
    manifest, wrong = collection_state()
    papers = {entry['key']: '' if entry['key'] in wrong else read_file(EXEMPLARS / (entry['key'] + '.tex'))
              for entry in manifest}
    return manifest, papers, wrong


def render_exemplars(manifest):
    """exemplars.md: the list of the collection for the sessions."""
    lines = ['# The collection of papers', '',
             f'{len(manifest)} research articles from refereed journals, each kept as the LaTeX source its authors '
             'wrote. A paper that a session is given stands in its folder as `exemplars/<key>.tex`.', '']
    for entry in manifest:
        authors = entry['authors'] if isinstance(entry['authors'], list) else [entry['authors']]
        lines += [f"## `{entry['key']}`: {entry['title']}", '',
                  f"{', '.join(map(str, authors))}. {entry['journal']}, {entry['year']}.", '',
                  f"Field: {entry['field']}. Pages: {entry['pages']}.", '',
                  f"Abstract: {collapsed(str(entry['abstract']))}", '',
                  f"Why it is in the collection: {entry['why']}", '']
    return '\n'.join(lines)


def likeness_papers(manifest, chosen):
    """The papers the plan did not choose, in the order the readings beside real papers take them.

    Those whose field is the field of a chosen paper come first; each group keeps the order of the manifest."""
    fields = {entry['field'] for entry in manifest if entry['key'] in chosen}
    rest = [entry for entry in manifest if entry['key'] not in chosen]
    return [e['key'] for e in rest if e['field'] in fields] + [e['key'] for e in rest if e['field'] not in fields]


def check_likeness(report):
    """The reasons the script cannot pass on a report of a reading beside real papers: its shape only.

    Whether a departure is real is for the readings to judge; no quotation is looked up."""
    problems = []
    bad = problems.append
    if not is_text(report.get('likeness')):
        bad('output/likeness.json: "likeness" is a text that is not empty')
    departures = report.get('departures')
    if not isinstance(departures, list):
        return problems + ['output/likeness.json: "departures" is an array, empty when there is no departure']
    for number, departure in enumerate(departures, 1):
        where = f'departure {number}'
        if not isinstance(departure, dict):
            bad(f'{where} is not an object with "where", "quote", "evidence" and "difference"')
            continue
        for field in ('where', 'difference'):
            if not is_text(departure.get(field)):
                bad(f'{where}: "{field}" is a text that is not empty')
        if not isinstance(departure.get('quote'), str):
            bad(f'{where}: "quote" is a text: a passage of paper.tex, or the empty string when something is missing')
        evidence = departure.get('evidence')
        if not isinstance(evidence, list) or not all(
                isinstance(item, dict) and isinstance(item.get('exemplar'), str) and isinstance(item.get('quote'), str)
                for item in evidence):
            bad(f'{where}: "evidence" is an array of objects, each with "exemplar" and "quote" as text')
    return problems


# ----------------------------------------------------------------------------- materials

def settling_proof(model):
    """The declaration whose formal proof settles the root: a proof of the root, or of its negation.

    Which proofs settle the root is knowledge.root_settlement's to say. Of several, the root's own proof is
    taken where it is one of them, and otherwise the first by name."""
    settlement = root_settlement(model)
    if settlement is None:
        raise Stop(f"the root is {model['root_state']}; the paper is written once the root is settled by a formal "
                   'proof (formal_proved or formal_refuted)')
    return model['root'] if model['root'] in settlement['proofs'] else settlement['proofs'][0]


def closing(draft, model):
    """The declarations that closed a gap of a draft and that the instance has, in the order of the gaps."""
    return list(dict.fromkeys(gap.get('closed_by') for gap in draft['gaps'] if gap.get('closed_by') in model['elements']))


def chosen_main(model, main):
    """The element that a run is told to take for the main result of the paper, when that changes anything.

    None when no element is named, or the one named is the declaration that settles the root, which
    is the main result of a paper anyway. Otherwise the element has to be a theorem of the instance
    whose proof is settled and formal, as everything the paper states is; the command stops when it
    is not."""
    if main is None or main == settling_proof(model):
        return None
    element = model['elements'].get(main)
    reason = ('the instance has no declaration of that name' if element is None
              else 'it is a definition' if element['kind'] != 'theorem'
              else None if element['settled'] and element['formal'] else 'its proof is not settled and formal')
    if reason:
        raise Stop(f'--main {main}: the main result of the paper is a theorem of the instance that is settled by a '
                   f'formal proof, and {reason}')
    return main


def settling(materials):
    """The declaration whose formal proof settles the root, as the materials name it.

    It is the main result of the paper unless another theorem was chosen for that (extract, `main`)."""
    return materials.get('settles', materials['main'])


def rests_on(elements, name, used):
    """Whether an element of the materials rests on another, through what the proofs name and the statements mention."""
    found, pending = {name}, [name]
    while pending:
        element = elements[pending.pop()]
        for below in element['uses'] + element['mentions']:
            if below in elements and below not in found:
                found.add(below)
                pending.append(below)
    return used != name and used in found


def extract(instance, model, further=(), main=None):
    """Everything the paper is written from: what the formal proof of the root rests on, with the records.

    The elements are those reached from the settling proof through what each proof names and each
    statement mentions. A statement with several proofs is followed through the declaration that
    the proof above it names, so the other proofs and what only they rest on stay out. The order is
    one of dependence: an element comes after everything it names or mentions.

    `main` names the theorem that the paper is built around when that is not the declaration that
    settles the root (chosen_main): a stronger theorem, as a rule, from which the root follows. The
    materials are then what that theorem rests on together with the settling declaration and what
    it rests on. "main" is the chosen theorem, "settles" names the settling declaration, and the
    element of that declaration carries "settles". The theorem is reached first and the settling
    declaration after it, since as a rule the second rests on the first. Without `main`, or when it
    is the settling declaration, the materials are exactly what they are without this parameter.

    `further` names declarations that the materials hold as well, with everything they rest on: in a
    paper that is written from a draft, the declarations that were added to the library to close a
    gap of the draft, which the proof of the root need not use. A statement among them is taken only
    when its own proof is settled and formal, as everything else in the materials is. They are
    reached before the settling proof, so the main result is still the last element, unless one of
    them rests on the main result and has to come after it. An element that the proof of the root
    does not rest on carries "outside", and the materials then name the further declarations under
    "further". Without `further` the materials are exactly what they are without this parameter."""
    instance = Path(instance)
    canon = Canon(instance)
    index = canon.load_index()['entries']
    elements = model['elements']
    settles = settling_proof(model)
    main = chosen_main(model, main) or settles
    further = [name for name in dict.fromkeys(further) if name in elements and name not in (main, settles)
               and (elements[name]['kind'] != 'theorem' or (elements[name]['settled'] and elements[name]['formal']))]

    def below(name):
        return sorted({u for u in elements[name]['uses'] + elements[name]['statement_uses'] if u in elements})

    order, seen = [], set()
    for start in (*further, main, settles):
        if start in seen:
            continue
        seen.add(start)
        stack = [(start, iter(below(start)))]
        while stack:
            name, rest = stack[-1]
            for used in rest:
                if used not in seen:
                    seen.add(used)
                    stack.append((used, iter(below(used))))
                    break
            else:
                order.append(name)
                stack.pop()
    # What the proof of the root and the main result rest on, to tell the elements that are here for a further
    # declaration alone.
    rested, pending = {main, settles}, [main, settles]
    while pending:
        for used in below(pending.pop()):
            if used not in rested:
                rested.add(used)
                pending.append(used)

    def sections_of(name):
        record = read_record(canon, name)
        return record['sections'] if record else {}

    def entry(name):
        element, sections = elements[name], sections_of(name)
        statement = element['kind'] == 'theorem'
        states = element['statement_of'] if statement and element['statement_of'] != name else None
        words, source = sections.get('Statement'), name
        if not words and states:
            words, source = sections_of(states).get('Statement'), states
        item = {'name': name, 'kind': 'statement' if statement else 'definition', 'weight': element['weight'],
                'short': element['short'], 'main': name == main, 'lean': element['statement'], 'states': states,
                'uses': [u for u in element['uses'] if u in elements],
                'mentions': [u for u in element['statement_uses'] if u in elements],
                'used_by': [n for n in order if name in elements[n]['uses'] + elements[n]['statement_uses']],
                'source': element['source'], 'description': sections.get('Description', element['description']),
                'statement': words or None, 'statement_from': source if words else None,
                'explanation': sections.get('Explanation'), 'proof': sections.get('Proof'),
                'literature': sections.get('Literature')}
        if statement:
            item.update(standing=element['standing'], settled=element['settled'], formal=element['formal'])
        else:
            text = (canon.lean / index[name]['file']).read_text(encoding='utf-8').replace('\r\n', '\n')
            item['definition_text'] = declaration_text(text, index[name]['span'])
        if name not in rested:
            item['outside'] = True
        if name == settles != main:
            item['settles'] = True
        return item

    understanding, review = read_question_account(canon, ROOT_QUESTION)
    bibliography = read_file(canon.bibliography) if canon.bibliography.is_file() else ''
    root = model['root']
    root_sections = sections_of(root)
    return {'revision': model['sequence'], 'root': {
                'name': root, 'state': model['root_state'], 'words': read_file(instance / 'root.md').strip(),
                'lean': elements[root]['statement'], 'statement': root_sections.get('Statement'),
                'explanation': root_sections.get('Explanation')},
            'main': main, 'axioms': elements[settles]['axioms'], 'allowed_axioms': model['allowed_axioms'],
            'understanding': understanding.strip(), 'understanding_review': review,
            'elements': [entry(name) for name in order],
            'bibliography': bibliography, 'bibliography_keys': BIB_ENTRY.findall(bibliography),
            'identifiers': sorted(set(elements) | {e['module'] for e in elements.values()}),
            **({'further': further} if further else {}), **({'settles': settles} if settles != main else {})}


def backquoted(values):
    return ', '.join('`' + value + '`' for value in values) or '(nothing)'


def main_lines(materials):
    """What the head of the materials says of a main result that is not the declaration that settles the root; no
    line when the settling declaration is the main result."""
    if 'settles' not in materials:
        return []
    main, settles = materials['main'], materials['settles']
    elements = {element['name']: element for element in materials['elements']}
    follows = (f'The proof of `{settles}` rests on it, so the root follows from the main result.'
               if rests_on(elements, settles, main) else
               f'The proof of `{settles}` does not rest on it: the two stand beside each other.')
    return ['## The main result of the paper', '',
            f'The main result of this paper is `{main}`, and not the declaration that settles the root. This theorem '
            'was chosen, before the paper was planned, as the one the paper is built around. ' + follows + ' The paper states '
            f'`{main}` as its main theorem, first in the introduction, and it states `{settles}` as a numbered '
            'statement as well, a corollary of the main theorem or a theorem beside it, so that the root stands in the '
            f'paper with its exact statement. The statement of `{settles}` is the one that says what the root says in '
            'words; the main theorem says what its own element says.', '']


def main_note(materials):
    """What a session that writes a plan is told beside the conditions under which the script accepts one, when
    the main result is not the declaration that settles the root; nothing otherwise."""
    if 'settles' not in materials:
        return ''
    main, settles = materials['main'], materials['settles']
    return (f' In this paper the main result is `{main}`, and the declaration that settles the root is another '
            f'element, `{settles}`; the head of the materials says so under "The main result of the paper". The main '
            f'theorem that the plan states first is therefore `{main}`. The script also requires that `{settles}` is a '
            'numbered statement, so that the paper states the root with its exact statement: a corollary where it '
            'follows from the main theorem in a few lines, and otherwise a theorem beside it. That statement, and not '
            'the main theorem, is the one that says what the root says in words (method, section "Every numbered '
            'statement says what its element says").')


def head_lines(materials):
    """The root, how it was settled, and the account of the problem as a whole, as lines of a text."""
    root = materials['root']
    proved = root['state'] == 'formal_proved'
    lines = ['## The root', '', 'The root in words, as it was fixed when the research began:', '',
             *('> ' + line for line in root['words'].splitlines()), '',
             'The root in Lean:', '', '```lean', 'theorem ' + root['lean'], '```', '',
             ('The root has been proved' if proved else 'The root has been refuted') + ' by a formal proof. '
             + (f"The declaration whose formal proof settles it is `{settling(materials)}`"
                + ('.' if proved else ', whose statement is the negation of the root.')),
             'Axioms that formal proof depends on: ' + (', '.join(materials['axioms']) or 'none')
             + '. Axioms the instance allows: ' + ', '.join(materials['allowed_axioms']) + '.', '']
    if settling(materials) != root['name']:
        for title, key in (("The statement in the root's record", 'statement'), ("The explanation in the root's record", 'explanation')):
            if root[key]:
                lines += [f'**{title}.**', '', root[key], '']
    lines += main_lines(materials)
    lines += ['## The understanding so far of the problem as a whole', '',
              materials['understanding'] or 'No account of the problem as a whole has been written.', '']
    if materials.get('understanding_review'):
        lines += ['### Review of the change that supplied this account', '', materials['understanding_review'], '']
    return lines


RECORD = (('Description', 'description'), ('Statement', 'statement'), ('Explanation', 'explanation'), ('Proof', 'proof'),
          ('Literature', 'literature'))
# How a text marks an element that the proof of the root does not rest on (extract, `further`).
OUTSIDE = ' · added for the draft of the paper'


def role_mark(element):
    """How a text marks the main result, and the declaration that settles the root when that is another element."""
    return (' · the main result' if element['main'] else '') + (' · settles the root' if element.get('settles') else '')


def order_note(materials):
    """What a text that lists the elements says of their number and their order, as one paragraph."""
    elements = materials['elements']
    note = (f'{len(elements)} elements in dependence order: each comes after everything its statement mentions and its '
            'proof names, ' + ('and the last is the main result.' if elements[-1]['main'] else
                               f"and the main result is `{materials['main']}`, which is not the last of them."))
    if 'settles' in materials:
        note += f" The declaration that settles the root is `{materials['settles']}`."
    if any(element.get('outside') for element in elements):
        note += (' The proof of the root rests on all of them except those marked as added for the draft of the paper. '
                 'These are declarations that the library received so that the paper can state what its draft asked '
                 'for, and what only they rest on; they are proved as everything else here is, and the paper may state '
                 'them.')
    return note


def element_lines(element, users=True):
    """One element as lines of a text, from the line that gives its kind: the Lean form, what it names, its record.

    Without `users` the elements that name this one are left out; a brief says in its own way where an
    element is used."""
    lines = [f"{element['kind']} · weight: {element['weight']}"
             + (f" · short name: {element['short']}" if element['short'] else '')
             + role_mark(element) + (OUTSIDE if element.get('outside') else ''), '']
    if element['kind'] == 'definition':
        lines += ['```lean', element['definition_text'], '```', '']
    else:
        lines += ['```lean', 'theorem ' + element['lean'], '```', '']
    if element.get('outside'):
        lines += ['The proof of the root does not rest on this element. The library received it, or what rests on it, '
                  'so that the paper can state what its draft asked for.', '']
    if element['states']:
        lines += [f"This declaration is another proof of the statement `{element['states']}`; the proof above it "
                  'names this declaration, so this is the proof the paper gives.', '']
    if element['source']:
        lines += [f"A result taken from the literature; bibliography key `{element['source']}`.", '']
    if element['kind'] == 'statement':
        if 'standing' in element:
            lines.append(f"At this revision this proof is {STANDINGS[element['standing']]}, "
                         + ('settled' if element['settled'] else 'unsettled') + ', and '
                         + ('formal.' if element['formal'] else 'not formal.'))
        lines.append(f"Its statement mentions {backquoted(element['mentions'])}. Its proof names {backquoted(element['uses'])}.")
    else:
        lines.append(f"It is defined from {backquoted(sorted(set(element['mentions'] + element['uses'])))}.")
    lines += ([f"Among these elements it is named or mentioned by {backquoted(element['used_by'])}."]
              if element['used_by'] and users else []) + ['']
    for title, key in RECORD:
        if element[key]:
            note = (f" (from the record of `{element['statement_from']}`)"
                    if key == 'statement' and element['statement_from'] != element['name'] else '')
            lines += [f'**{title}{note}.**', '', element[key], '']
    return lines


def summary_lines(element, users=True):
    """One element by what it says, as lines of a text: its kind, its Lean form, what it names, its description
    and its statement in words; for a result from the literature also what the record says of the source.

    It is the short form of element_lines, for a text that gives many elements and leaves their
    explanations and proofs to the files of the elements. `users` adds the elements that name this one."""
    lines = [f"{element['kind']} · weight: {element['weight']}"
             + (f" · short name: {element['short']}" if element['short'] else '')
             + role_mark(element) + (OUTSIDE if element.get('outside') else '')
             + (f" · another proof of the statement `{element['states']}`, and the one the paper gives" if element['states'] else '')
             + (f" · a result taken from the literature, bibliography key `{element['source']}`" if element['source'] else ''),
             '', '```lean', element['definition_text'] if element['kind'] == 'definition' else 'theorem ' + element['lean'],
             '```', '']
    named = (f"Its statement mentions {backquoted(element['mentions'])}. Its proof names {backquoted(element['uses'])}."
             if element['kind'] == 'statement'
             else f"It is defined from {backquoted(sorted(set(element['mentions'] + element['uses'])))}.")
    lines += [named + (f" It is named or mentioned by {backquoted(element['used_by'])}." if users and element['used_by'] else ''), '']
    for title, key in RECORD:
        if element[key] and (key in ('description', 'statement') or (key == 'literature' and element['source'])):
            note = (f" (from the record of `{element['statement_from']}`)"
                    if key == 'statement' and element['statement_from'] != element['name'] else '')
            lines += [f'**{title}{note}.** ' + element[key].strip(), '']
    return lines


def bibliography_lines(materials):
    return ['## Bibliography', ''] + (['```bibtex', materials['bibliography'].strip(), '```']
                                      if materials['bibliography'].strip()
                                      else ['The canon has no bibliography: the paper cites nothing.'])


def lean_names_note(materials):
    return (f"Taken by script from the canon at revision {materials['revision']}. A name between backquotes, such as "
            f"`{materials['root']['name']}`, is the name of a Lean declaration. It identifies an element here and in the "
            'plan, and it does not appear in the paper.')


def render_materials(materials):
    """The materials as one text: everything the paper is written from. It is kept beside the paper.

    No session is given this text. The planning session receives the digest (render_digest), a writing
    session the brief of its section (render_brief), and both have the record of every element as a
    file of its own (record_files)."""
    lines = ['# Materials for the paper', '', lean_names_note(materials), '', *head_lines(materials),
             '## The elements the proof rests on', '',
             order_note(materials), '']
    for number, element in enumerate(materials['elements'], 1):
        lines += [f"### {number}. `{element['name']}`", '', *element_lines(element)]
    return '\n'.join(lines + bibliography_lines(materials)) + '\n'


def element_files(materials):
    """The file that holds the record of each element in the folder of a session, by the name of the element.

    The file is named after the element. Two names that a file system would not tell apart, because they
    differ only in the case of a letter or in a character that a file name cannot hold, receive a number."""
    files, taken = {}, set()
    for element in materials['elements']:
        base = re.sub(r'[^A-Za-z0-9_.-]', '_', element['name'])
        name, number = base, 1
        while name.lower() in taken:
            number += 1
            name = f'{base}-{number}'
        taken.add(name.lower())
        files[element['name']] = f'elements/{name}.md'
    return files


def record_files(materials):
    """What a session that works from the records finds in its folder besides the files of its own task.

    `root.md` is the head of the materials: the root, its record and the account of the problem as a
    whole. `elements/` holds the full record of every element, one file each, and `elements.md` lists
    them with their files."""
    files, note = element_files(materials), lean_names_note(materials)
    listed = ['# The elements the proof rests on', '', note, '',
              order_note(materials) + ' Each line gives the name, the kind, the weight, the short '
              'name where the record has one, and the file that holds the full record.', '']
    found = {'root.md': '\n'.join(['# The root and the account of the problem', '', note, '',
                                    *head_lines(materials)]).rstrip('\n') + '\n'}
    for element in materials['elements']:
        listed.append(f"- `{element['name']}` · {element['kind']} · {element['weight']}"
                      + (f" · {element['short']}" if element['short'] else '')
                      + role_mark(element) + (OUTSIDE if element.get('outside') else '')
                      + f" · `{files[element['name']]}`")
        found[files[element['name']]] = '\n'.join([f"# `{element['name']}`", '', *element_lines(element)]).rstrip('\n') + '\n'
    found['elements.md'] = '\n'.join(listed) + '\n'
    return found


def render_digest(materials):
    """The materials for the session that plans the paper: every element by what it says, and the proof as a whole.

    The planning session decides how each element appears in the paper, for which it needs what each
    element says and what it rests on. The explanations and the proofs in words are most of the
    materials; they are left to the files of the elements, and their lengths are given here. Two
    records are given in full, because the account of the whole proof is in them: the root's, and that
    of the declaration that settles the root. When the main result of the paper is another element,
    its record is given in full as well, before that of the settling declaration."""
    files = element_files(materials)
    by_name = {element['name']: element for element in materials['elements']}
    main, chosen = by_name[settling(materials)], 'settles' in materials
    lines = ['# Digest of the materials for the paper', '', lean_names_note(materials), '',
             'This digest gives every element that the proof of the root rests on by what it says: its name, its kind '
             'and its weight, its short name, its Lean form, what it names and what names it, its description and its '
             'statement in words. It leaves out the explanation and the proof in words of each element and gives their '
             'lengths in characters instead, and it leaves out the standing of each proof, which is the same for all: '
             'everything here is settled by a formal proof. The full record of every element is in a file of its own, which the digest '
             'names at the element. '
             + ('The records of the main result of the paper and of the declaration that settles the root are given '
                if chosen else 'The record of the declaration that settles the root is given ')
             + 'in full, before the list of the elements: the account of the whole proof is there.', '',
             *head_lines(materials),
             *(['## The main result of the paper, with its record in full', '', f"### `{materials['main']}`", '',
                *element_lines(by_name[materials['main']])] if chosen else []),
             '## The declaration that settles the root, with its record in full', '',
             f"### `{main['name']}`", '', *element_lines(main),
             '## The elements the proof rests on', '',
             order_note(materials), '']
    for number, element in enumerate(materials['elements'], 1):
        lengths =[f'{title} in words: {len(element[key])} characters' if element[key] else f'no {title} in words'
                   for title, key in (('explanation', 'explanation'), ('proof', 'proof'))]
        lines += [f"### {number}. `{element['name']}`", '', *summary_lines(element),
                  f"Full record: `{files[element['name']]}` ({'; '.join(lengths)})."
                  + (' It is given in full above.' if element['main'] or element.get('settles') else ''), '']
    return '\n'.join(lines + bibliography_lines(materials)) + '\n'


# ----------------------------------------------------------------------------- the plan

def stands_in(element, other, elements):
    """Whether `other` can stand where `element` is not stated: the method's cases of what the paper leaves out."""
    if element['kind'] == 'definition':
        # One of two definitions that an element states to agree.
        return other['kind'] == 'definition' and any(
            e['kind'] == 'statement' and {element['name'], other['name']} <= set(e['mentions']) for e in elements.values())
    return (other['name'] in element['uses']  # the consequence a superseded statement left: its proof names the new one
            or (element['states'] or element['name']) == (other['states'] or other['name'])  # two proofs of one statement
            or (other['kind'] == 'definition' and other['name'] in element['mentions']))  # two definitions agree


def choice_problems(plan, keys):
    """The reasons the papers a plan chooses are not CHOSEN_PAPERS different keys of the collection."""
    chosen = plan.get('exemplars')
    if not isinstance(chosen, list) or not all(isinstance(key, str) for key in chosen):
        return [f'"exemplars" is an array of the keys of the {CHOSEN_PAPERS} papers of exemplars.md that this paper is '
                'written like']
    problems = []
    unknown = [key for key in chosen if key not in keys]
    if unknown:
        problems.append('"exemplars" names keys that are not keys of exemplars.md: ' + ', '.join(unknown))
    repeated = sorted({key for key in chosen if chosen.count(key) > 1})
    if repeated:
        problems.append('"exemplars" names a paper more than once: ' + ', '.join(repeated))
    if len(chosen) != CHOSEN_PAPERS:
        problems.append(f'"exemplars" names {len(chosen)} papers; it names exactly {CHOSEN_PAPERS} different ones')
    return problems


def check_plan(materials, plan, keys):
    """The reasons the script cannot carry a plan out, as sentences for the next planning session.

    `keys` are the keys of the collection, from which the plan chooses its papers."""
    problems = []
    bad = problems.append
    elements = {e['name']: e for e in materials['elements']}
    if not isinstance(plan, dict):
        return ['plan.json holds one JSON object']
    for key in ('title', 'outline'):
        if not is_text(plan.get(key)):
            bad(f'"{key}" is a nonempty text')
    if 'short_title' in plan and not is_text(plan['short_title']):
        bad('"short_title", when the plan has it, is a nonempty text')
    keywords = plan.get('keywords', [])
    if not isinstance(keywords, list) or not all(is_text(word) and all(ord(char) < 128 for char in word) for word in keywords):
        bad('"keywords", when the plan has it, is an array of key words and phrases, each a nonempty text in ASCII')
        keywords = []
    problems += choice_problems(plan, keys)
    sections, statements, others = plan.get('sections'), plan.get('statements'), plan.get('others')
    for key, value in (('sections', sections), ('statements', statements), ('others', others)):
        if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
            return problems + [f'"{key}" is an array of objects']
    if not sections:
        return problems + ['"sections" names at least the introduction']
    for section in sections:
        if not (isinstance(section.get('id'), str) and SECTION_ID.fullmatch(section['id'])) or section['id'] == 'abstract':
            bad(f"section id {section.get('id')!r}: a short lowercase word ([a-z][a-z0-9-]*) other than \"abstract\"")
        if not is_text(section.get('title')) or not is_text(section.get('content')):
            bad(f"section {section.get('id')!r} needs a \"title\" and a \"content\"")
        # The writer of a section reads these papers whole, so the plan names them for every section.
        papers, chosen = section.get('exemplars'), plan.get('exemplars')
        if not (isinstance(papers, list) and len(papers) == SECTION_PAPERS and all(isinstance(key, str) for key in papers)
                and len(set(papers)) == SECTION_PAPERS and isinstance(chosen, list) and all(key in chosen for key in papers)):
            bad(f"section {section.get('id')!r}: \"exemplars\" names {SECTION_PAPERS} different papers among those of the "
                'plan\'s own "exemplars": the ones closest to a section of this kind')
    # One object has one notation, and the plan fixes it: a writer does not see how another section names an object.
    notation, symbols = plan.get('notation'), {}
    if not isinstance(notation, list) or not all(isinstance(entry, dict) and is_text(entry.get('symbol'))
                                                 and is_text(entry.get('meaning')) for entry in notation):
        bad('"notation" is an array of objects, each with a "symbol" and a "meaning"')
        notation = []
    for entry in notation:
        listed = entry.get('elements', [])
        if not isinstance(listed, list) or not all(isinstance(name, str) for name in listed):
            bad(f"notation {entry['symbol']}: \"elements\" is an array of the names of the definitions whose object the "
                'entry denotes, empty when it denotes none')
            continue
        for name in listed:
            if name not in elements or elements[name]['kind'] != 'definition':
                bad(f"notation {entry['symbol']}: {name!r} is not a definition of the materials")
            elif name in symbols:
                bad(f'{name} is named in two entries of "notation"; one object has one notation')
            else:
                symbols[name] = entry
    # A draft names the results that the paper would cite if their records named a source. The plan of a paper
    # that is not drafted has no such list.
    wanted, listed = plan.get('citations', []), set()
    if not isinstance(wanted, list) or not all(isinstance(entry, dict) for entry in wanted):
        bad('"citations", when the plan has it, is an array of objects, each with an "element", a "result" and a "reason"')
        wanted = []
    for entry in wanted:
        name = entry.get('element')
        if name not in elements or elements[name]['kind'] != 'statement':
            bad(f'citations: {name!r} is not a statement of the materials')
        elif elements[name]['source']:
            bad(f"citations: {name} has the source {elements[name]['source']} in its record, so the plan cites it already; "
                '"citations" lists results whose record names no source')
        elif name in listed:
            bad(f'citations: {name} is listed twice')
        elif not is_text(entry.get('result')) or not is_text(entry.get('reason')):
            bad(f'citations: {name} needs a "result", the name under which the result is known, and a "reason"')
        listed.add(name)
    order = {section.get('id'): number for number, section in enumerate(sections)}
    if len(order) != len(sections):
        bad('two sections have the same id')
    # A formula that more than one section needs has one place and one label, which the plan fixes: the writers do
    # not see each other's text, so nothing else lets the second of them refer to the formula of the first.
    displays, shared = plan.get('displays', []), set()
    if not isinstance(displays, list) or not all(isinstance(entry, dict) for entry in displays):
        bad('"displays", when the plan has it, is an array of objects, each with "label", "section", "element", '
            '"formula" and "used_in"')
        displays = []
    for entry in displays:
        label, owner, users = entry.get('label'), entry.get('section'), entry.get('used_in')
        if not isinstance(owner, str) or owner not in order:
            bad(f'displays: {label!r}: "section" is the id of the section that displays the formula')
            continue
        if not (isinstance(label, str) and LABEL_FORM.fullmatch(label) and label.startswith(f'eq:{owner}-')
                and label not in shared):
            bad(f'displays: the label {label!r} begins with eq:{owner}-, the id of the section that displays the formula, '
                'and is used once')
        shared.add(label)
        if not isinstance(entry.get('element'), str) or entry['element'] not in elements:
            bad(f"displays: {label!r}: \"element\" is the name of the element of the materials that states the formula")
        if not is_text(entry.get('formula')):
            bad(f'displays: {label!r}: "formula" is the formula in LaTeX')
        if not (isinstance(users, list) and users and all(isinstance(user, str) and user in order
                                                           and order[user] > order[owner] for user in users)):
            bad(f'displays: {label!r}: "used_in" lists the ids of the sections after {owner} that refer to the formula; '
                'the section that displays it is the first that needs it')
    # The titles stand in the manuscript as the plan has them, and a repair keeps the plan. A Lean name or the
    # word Lean in a title is therefore reported here, where a planning session can still change it. So is a
    # character that is not ASCII in the title of the paper, in its short title or in the title of a section. The
    # machine checks of the manuscript report such a character in the title of the paper as they do in a part
    # (machine_findings) and do not look at the other two, where TeX can fail on it; no repair session can change
    # any of the three.
    pattern = identifier_pattern(materials['identifiers'])
    titles = [('the title', plan.get('title')), ('the short title', plan.get('short_title'))] \
        + [(f"the title of section {s.get('id')!r}", s.get('title')) for s in sections] \
        + [('"keywords"', word) for word in keywords]
    for where, title in titles:
        if is_text(title):
            plain = title.replace('\\_', '_')
            found = sorted({m[0] for m in pattern.finditer(plain)} | {m[0] for m in LEAN_WORDS.finditer(plain)})
            if found:
                bad(f'{where} has ' + ', '.join(found) + '; the paper names no declaration of the canon and does not '
                    'mention Lean (method, section "The implementation does not show")')
    for where, title in titles[:2 + len(sections)]:  # the title, the short title and the titles of the sections
        strange = sorted({char for char in title if ord(char) > 127}) if is_text(title) else []
        if strange:
            bad(f'{where} is written in ASCII, as the parts of the manuscript are; write these characters as LaTeX: '
                + ' '.join(strange))
    placed = {}
    for item in statements + others:
        name = item.get('element')
        if name not in elements:
            bad(f'{name!r} is not an element of the materials')
        elif name in placed:
            bad(f'{name} appears twice in the plan')
        else:
            placed[name] = item
    missing = [name for name in elements if name not in placed]
    if missing:
        bad('the plan says nothing about these elements of the materials: ' + ', '.join(missing))
    if problems:
        return problems
    numbered = {item['element']: number for number, item in enumerate(statements)}

    def proof_of(item):
        """Where the proof of a numbered statement is written: a section id, 'cited', or None for a definition."""
        return item.get('proof', item.get('section')) if elements[item['element']]['kind'] == 'statement' else None

    def reach(name, first=('uses', 'mentions'), through=lambda n: True):
        """What an element rests on, following its `first` edges and then every edge of the elements `through` lets pass."""
        found, pending = set(), [u for key in first for u in elements[name][key]]
        while pending:
            used = pending.pop()
            if used in found or used == name:
                continue
            found.add(used)
            if through(used):
                pending += elements[used]['uses'] + elements[used]['mentions']
        return found

    labels = set()
    for number, item in enumerate(statements):
        name, element = item['element'], elements[item['element']]
        kind, label, section = item.get('kind'), item.get('label'), item.get('section')
        if kind not in NUMBERED:
            bad(f'{name}: "kind" is one of ' + ', '.join(NUMBERED))
        elif (kind == 'definition') != (element['kind'] == 'definition'):
            bad(f"{name} is a {element['kind']}; a definition is numbered as a definition and a statement as a "
                'theorem, proposition, lemma or corollary')
        if isinstance(label, str) and LABEL_FORM.fullmatch(label) and not label.startswith('sec:') and label not in labels:
            labels.add(label)
        else:
            bad(f'{name}: "label" {label!r} is a prefix, a colon and a lowercase word, used once; "sec:" is the script\'s')
        if section not in order:
            bad(f'{name}: "section" {section!r} is not the id of a section')
            continue
        if number and order.get(statements[number - 1].get('section'), 0) > order[section]:
            bad(f'{name}: "statements" lists the numbered statements in the order of the paper, section by section')
        proof = proof_of(item)
        if element['kind'] == 'definition' and 'proof' in item:
            bad(f'{name} is a definition and has no "proof"')
        if element['source'] and element['kind'] == 'statement' and proof != 'cited':
            bad(f'{name} is taken from the literature: its "proof" is "cited"')
        if proof == 'cited' and not element['source']:
            bad(f'{name} has no source in the literature; it cannot be "cited" in place of a proof')
        if proof not in (None, 'cited') and (proof not in order or order[proof] < order[section]):
            bad(f'{name}: "proof" {proof!r} is the id of its own section or of a later one')
        if element['weight'] == 'step' and not is_text(item.get('reason')):
            bad(f'{name} has the weight step and is numbered; say why in "reason"')
    for item in others:
        name, element, treatment = item['element'], elements[item['element']], item.get('treatment')
        if treatment == 'absorbed':
            into = item.get('into')
            if not isinstance(into, list) or not into:
                bad(f'{name}: "into" lists the numbered elements or the section ids it is written into')
            for target in into if isinstance(into, list) else []:
                if target in order:
                    continue
                if target not in numbered:
                    bad(f'{name} is absorbed into {target!r}, which is neither a numbered element nor a section id')
                elif name not in reach(target):
                    bad(f'{name} is absorbed into {target}, which does not rest on it')
        elif treatment == 'cited':
            if not element['source']:
                bad(f'{name} has no source in the literature; it cannot be cited')
            if item.get('section') not in order:
                bad(f'{name}: "section" is the id of the section that cites it')
        elif treatment == 'not_stated':
            other = item.get('by')
            if other not in elements or other == name or placed[other].get('treatment') == 'not_stated':
                bad(f'{name}: "by" names the element of the materials that stands in its place and is itself in the paper')
            elif not stands_in(element, elements[other], elements):
                bad(f'{name} is not stated, but {other} does not stand in its place: the proof of {name} does not '
                    f'name it, the two do not prove one statement, and no element states that two definitions agree')
        else:
            bad(f'{name}: "treatment" is absorbed, cited or not_stated')
        if (element['weight'] == 'unit' or treatment == 'not_stated') and not is_text(item.get('reason')):
            bad(f'{name}: a unit that is not numbered and an element that is not stated need a "reason"')
    main = materials['main']
    leading = next((number for number, item in enumerate(statements) if item.get('kind') != 'definition'), None)
    if main not in numbered or statements[numbered[main]].get('kind') != 'theorem' \
            or statements[numbered[main]].get('section') != sections[0]['id'] or leading != numbered[main]:
        bad(f'the main result {main} is a theorem stated in the first section, before every other theorem, '
            'proposition, lemma and corollary')
    # When the paper is built around another theorem than the one that settles the root, the root still stands in
    # the paper with its exact statement.
    if 'settles' in materials and materials['settles'] not in numbered:
        bad(f"the declaration that settles the root, {materials['settles']}, is a numbered statement: the paper states "
            f'the root with its exact statement, as a corollary of the main theorem {main} or as a theorem beside it')
    if problems:
        return problems
    passes = lambda name: name not in numbered
    for number, item in enumerate(statements):
        name, proof = item['element'], proof_of(item)
        for needed in sorted(reach(name, ('mentions',), passes) & set(numbered)):
            if numbered[needed] > number:
                bad(f'{name} is stated before {needed}, which its statement mentions')
        if proof in (None, 'cited'):
            continue
        for needed in sorted(reach(name, through=passes) & set(numbered)):
            where = statements[numbered[needed]]
            late = order[where['section']] > order[proof] if proof != item['section'] else numbered[needed] > number
            if late:
                bad(f'the proof of {name} comes before the statement of {needed}, which it rests on')
    if problems:
        return problems
    # Sections are written side by side. An object that the writers of two sections meet is named alike in both
    # only if the plan names it. For the definitions of the materials the script can see which sections meet them.
    layout = Layout(materials, plan)
    for name, element in elements.items():
        met = layout.sections_of(name)
        if element['kind'] == 'definition' and name not in symbols and len(met) > 1 \
                and placed[name].get('treatment') != 'not_stated':
            bad(f'the definition {name} is met by the writers of the sections ' + ', '.join(met) + ', who do not see each '
                'other\'s text, and no entry of "notation" names it in its "elements"; give the symbol or the name under '
                'which the paper knows this object')
    return problems


class Layout:
    """Where a plan puts each element of the materials, section by section; the plan has passed check_plan.

    A section's own elements are those the plan has it state, prove, absorb or cite. `full` are the
    elements whose whole record the writer of a section is given, and `cited` those it is given by
    their statements: the elements of other sections that the first ones name."""

    def __init__(self, materials, plan):
        self.plan, self.main = plan, materials['main']
        self.elements = {element['name']: element for element in materials['elements']}  # in dependence order
        self.files = element_files(materials)
        self.numbered = {item['element']: item for item in plan['statements']}
        self.others = {item['element']: item for item in plan['others']}
        self.ids = [section['id'] for section in plan['sections']]
        self.symbols = {name: entry for entry in plan.get('notation') or [] for name in entry.get('elements') or []}
        own = {sid: set() for sid in self.ids}
        for name in self.elements:
            for sid in self.homes(name):
                own[sid].add(name)
        self.own, self.full, self.cited = {}, {}, {}
        for number, sid in enumerate(self.ids):
            # An element that the paper does not state is written nowhere, so it has no section. A section whose
            # elements name it has its record, with the element that stands in its place.
            self.spread(own[sid], sid, lambda name: self.treatment(name) == 'not_stated')
            # A step that another section absorbs has no number by which this section could refer to it. Where a
            # proof of this section uses it, its content is written at that place, so the record is given in full.
            full = set(own[sid])
            self.spread(full, sid, lambda name: self.treatment(name) == 'absorbed' and self.elements[name]['kind'] == 'statement')
            if number == 0:
                # The introduction outlines the proof from the explanations of the main result and of what its
                # proof names directly (method, section "The parts of the paper").
                self.drawn = set(self.elements[self.main]['uses']) - full
                full |= self.drawn
            cited = {used for name in full for used in self.named(name, sid)} - full
            self.own[sid], self.full[sid], self.cited[sid] = ([name for name in self.elements if name in chosen]
                                                              for chosen in (own[sid], full, cited))

    def named(self, name, sid):
        """What the writer of a section meets through an element: what its statement mentions and its proof names.

        Where the section does not write the proof, because the plan puts it into another section or the
        result is cited, the writer meets only what the statement mentions."""
        element = self.elements[name]
        item = self.numbered.get(name) or self.others[name]
        elsewhere = (self.proof_of(item) not in (None, sid)) if name in self.numbered else item['treatment'] == 'cited'
        return element['mentions'] + ([] if elsewhere else element['uses'])

    def spread(self, names, sid, wanted):
        """Add to `names` the elements that its members name and that `wanted` accepts, and those that these name."""
        pending = list(names)
        while pending:
            for used in self.named(pending.pop(), sid):
                if used not in names and wanted(used):
                    names.add(used)
                    pending.append(used)

    def treatment(self, name):
        return 'numbered' if name in self.numbered else self.others[name]['treatment']

    def proof_of(self, item):
        """Where the proof of a numbered statement is written: a section id, 'cited', or None for a definition."""
        return item.get('proof', item['section']) if self.elements[item['element']]['kind'] == 'statement' else None

    def hosts(self, name, target):
        """The sections in which an element absorbed into `target` is written: the section itself, or those of a numbered element.

        A step is written into the proof of the numbered statement that absorbs it. A definition is
        also needed where that statement is stated."""
        if target in self.ids:
            return [target]
        host = self.numbered[target]
        proof = self.proof_of(host)
        if proof in (None, 'cited'):
            return [host['section']]
        return [host['section'], proof] if self.elements[name]['kind'] == 'definition' and proof != host['section'] else [proof]

    def homes(self, name):
        """The sections in which the plan has an element written: stated, proved, absorbed or cited."""
        if name in self.numbered:
            item = self.numbered[name]
            proof = self.proof_of(item)
            return [item['section']] + ([proof] if proof not in (None, 'cited', item['section']) else [])
        item = self.others[name]
        if item['treatment'] == 'cited':
            return [item['section']]
        if item['treatment'] == 'absorbed':
            return list(dict.fromkeys(sid for target in item['into'] for sid in self.hosts(name, target)))
        return []

    def called(self, name):
        item = self.numbered[name]
        return f"{item['kind']} `{item['label']}`"

    def sections_of(self, name):
        """The sections whose writers meet an element: in the record they have in full, or by its statement."""
        return [sid for sid in self.ids if name in self.full[sid] or name in self.cited[sid]]

    def placement(self, name):
        """Where the paper has an element, in words for a writer of another section."""
        if name in self.numbered:
            item = self.numbered[name]
            proof = self.proof_of(item)
            return (f"{self.called(name)}, stated in section `{item['section']}`"
                    + (' with its citation and not proved' if proof == 'cited'
                       else f' and proved in section `{proof}`' if proof not in (None, item['section']) else ''))
        item = self.others[name]
        if item['treatment'] == 'cited':
            return (f"it has no number; section `{item['section']}` cites it in its running text, as a result of "
                    f"`{self.elements[name]['source']}`")
        if item['treatment'] == 'absorbed':
            verb = 'defined' if self.elements[name]['kind'] == 'definition' else 'written'
            places = [f'in the running text of section `{target}`' if target in self.ids
                      else f"with {self.called(target)} (section `{'`, `'.join(self.hosts(name, target))}`)"
                      for target in item['into']]
            return f'it has no number; it is {verb} ' + ' and '.join(places)
        return f"the paper does not state it; `{item['by']}` stands in its place ({self.placement(item['by'])})"

    def role(self, name, sid):
        """What a section does with an element whose record it has in full, as a sentence for its writer."""
        if name in self.numbered:
            item = self.numbered[name]
            proof = self.proof_of(item)
            if item['section'] == sid:
                return (f'This section states it as {self.called(name)}'
                        + ('.' if proof is None else '; it is cited and not proved.' if proof == 'cited'
                           else '; its proof follows it.' if proof == sid else f'; its proof is written in section `{proof}`.'))
            if proof == sid:
                return f"This section proves it; it is stated as {self.called(name)} in section `{item['section']}`."
        else:
            item = self.others[name]
            if item['treatment'] == 'cited' and item['section'] == sid:
                return 'This section cites it in its running text; it has no number.'
            if item['treatment'] == 'not_stated':
                return (f"The paper does not state it; `{item['by']}` stands in its place ({self.placement(item['by'])}). "
                        'Where a proof used it, the paper calls that element, with a clause on how the case that is '
                        'needed follows if that is not immediate.')
            here = [target for target in item.get('into', []) if sid in self.hosts(name, target)]
            if here:
                # An object is defined once: where the plan writes a definition into several sections, in the first.
                homes = sorted(self.homes(name), key=self.ids.index)
                once = ('' if self.elements[name]['kind'] != 'definition' or len(homes) < 2
                        else ' The plan writes it into other sections as well, and this one is the first of them in the '
                             'order of the paper: this section defines the object.' if homes[0] == sid
                        else f' Section `{homes[0]}` comes before this one in the paper and defines the object; this '
                             'section uses it under the notation of the plan and does not define it a second time.')
                return ('This section writes it into ' + ' and into '.join(
                    'its running text' if target == sid else self.called(target) for target in here)
                        + '; it has no number.' + once)
        reason = ('The proof of the main result names it directly, and the introduction draws on its explanation.'
                  if sid == self.ids[0] and name in self.drawn else
                  'This section cannot refer to it by a number; where a proof of this section uses it, its content is '
                  'written at that place.')
        return f'It belongs to another section: {self.placement(name)}. {reason}'

    def used_elsewhere(self, name, sid):
        """The places in other sections where an element is used: the numbered statements and the running texts."""
        places = []
        for user in self.elements[name]['used_by']:
            if user in self.numbered:
                item = self.numbered[user]
                proof = self.proof_of(item)
                where = [(self.called(user), proof if proof not in (None, 'cited') else item['section'])]
            elif self.others[user]['treatment'] == 'absorbed':
                where = [('the running text', target) if target in self.ids else (self.called(target), host)
                         for target in self.others[user]['into'] for host in self.hosts(user, target)]
            else:
                where = []
            places += [f'{what} (section `{section}`)' for what, section in where if section != sid]
        return list(dict.fromkeys(places))

    def known_as(self, name):
        """The notation of the plan for an element, as a sentence, or nothing."""
        entry = self.symbols.get(name)
        return [f"The paper writes {entry['symbol'].strip()} for it: {entry['meaning'].strip().rstrip('.')}."] if entry else []

    def assignment(self, sid):
        """What the plan puts into one section, as lines for the session that writes it."""
        lines = []
        for item in self.plan['statements']:
            proof = self.proof_of(item)
            if item['section'] == sid:
                tail = ('' if proof is None else '; it is cited and not proved' if proof == 'cited'
                        else '; its proof follows it' if proof == sid else f'; its proof is written in section `{proof}`')
                lines.append(f"- stated here: {self.called(item['element'])}, which states the element `{item['element']}`{tail}")
            elif proof == sid:
                lines.append(f"- proved here: {self.called(item['element'])} (`{item['element']}`), stated in section `{item['section']}`")
        for item in self.plan['others']:
            if item['treatment'] == 'cited' and item['section'] == sid:
                lines.append(f"- cited in the running text: `{item['element']}`")
            into = item.get('into', []) if item['treatment'] == 'absorbed' else []
            if sid in into:
                lines.append(f"- written into the running text: `{item['element']}`")
            hosts = [self.called(target) for target in into if target not in self.ids and sid in self.hosts(item['element'], target)]
            if hosts:
                lines.append(f"- absorbed into {' and '.join(hosts)}: `{item['element']}`")
        lines = lines or ['- the plan places no element in this section']
        for name in self.own[sid]:
            if self.treatment(name) == 'not_stated':
                lines.append(f"- stated nowhere in the paper: `{name}`; `{self.others[name]['by']}` stands in its place")
        return lines


def drafted_lines(plan, section, draft):
    """The statements and the formulas of one section as a draft has them, as lines of its brief; none without them.

    The draft was compared with the library before the paper is written, so the brief gives each text
    with the element that states it and says that it stands as drafted. A statement belongs to the
    section that states it now, which the plan says; a formula to the section it was drafted for."""
    stated = {item['label']: item for item in plan['statements'] if item['section'] == section['id']}
    statements = [entry for entry in draft.get('statements', [])
                  if entry.get('label') in stated and not entry.get('cut') and is_text(entry.get('text'))]
    formulas = [entry for entry in draft.get('formulas', [])
                if entry.get('section') == section['id'] and not entry.get('cut') and is_text(entry.get('text'))]
    if not statements and not formulas:
        return []
    lines = ['## The statements and formulas of this section as they were drafted', '',
             'Before this paper was written, a session drafted the numbered statements of this section and the '
             'displayed formulas that its later proofs refer to. Each was then compared with the element named with it, '
             'and where the two differed the library or the draft was changed until they said the same. The library '
             'has not changed since, so each text below says exactly what its element says. It stands in the section '
             'as it is drafted here: the same objects, hypotheses, quantifiers, ranges and conclusion, and the same '
             'formula. The words around a formula are the writer\'s, and a statement may be worded otherwise where '
             'the sentence requires it, as long as it says the same. A text that says more than the draft is not '
             'covered by the library, and the library cannot be changed now.', '']
    for entry in statements:
        item = stated[entry['label']]
        lines += [f"- {item['kind']} `{entry['label']}`, which states the element `{item['element']}`:", '',
                  *('  ' + line for line in entry['text'].strip().splitlines()), '']
    for entry in formulas:
        where = (f"in the proof of `{entry['host']}`" if is_text(entry.get('host')) else 'in the running text')
        states = (f", which says what the element `{entry['element']}` states" if is_text(entry.get('element')) else '')
        lines += [f"- the displayed formula with the label `{entry.get('label')}`, {where}{states}:", '',
                  *('  ' + line for line in entry['text'].strip().splitlines()), '']
    return lines


def display_lines(plan, section):
    """The displayed formulas that several sections use, as lines of the brief of one section; none when it has none.

    The plan gives each such formula one section that displays it and one label (check_plan). The
    brief tells the section that owns a formula to display it under that label, and every section
    that uses it to refer to it and not to display it again."""
    sid = section['id']
    own = [entry for entry in plan.get('displays') or [] if entry['section'] == sid]
    used = [entry for entry in plan.get('displays') or [] if sid in entry['used_in']]
    if not own and not used:
        return []
    lines = ['## Displayed formulas that several sections use', '',
             'The sections are written side by side, so a formula that two sections need would be displayed twice, '
             'under two numbers, and the reader would meet the same formula as two. The plan therefore gives each '
             'such formula one place and one label. The section that the plan names displays the formula once, in '
             '`equation` or `align`, with exactly that label. Every other section refers to it with `\\eqref` and does '
             'not display it again. These labels exist whoever writes the other sections, like the labels of the '
             'numbered statements.', '']
    for entry in own:
        lines += [f"- This section displays the formula below with `\\label{{{entry['label']}}}`. The element "
                  f"`{entry['element']}` states it, and the sections " + ', '.join(f'`{user}`' for user in entry['used_in'])
                  + ' refer to it:', '', *('  ' + line for line in entry['formula'].strip().splitlines()), '']
    for entry in used:
        lines += [f"- The section `{entry['section']}` displays the formula below, which the element "
                  f"`{entry['element']}` states. This section refers to it as `\\eqref{{{entry['label']}}}`:", '',
                  *('  ' + line for line in entry['formula'].strip().splitlines()), '']
    return lines


def instance_lines(section, draft, layout, keys):
    """The results of one section that a cited general theorem contains, as lines of its brief; none without them.

    Before the library was frozen, the session that looks for sources found for some results a
    general theorem of which the result is an instance, and wrote down the specialisation. The draft
    carries these under "instances" (read_draft). The brief gives each to the section that writes
    the proof of the result, or into whose proofs the plan absorbs it. `keys` are the keys of the
    bibliography; a theorem whose work is not in it cannot be cited and is left out."""
    sid, found = section['id'], []
    for entry in draft.get('instances') or []:
        name = entry.get('element')
        if entry.get('key') not in keys:
            continue
        if name in layout.numbered and layout.proof_of(layout.numbered[name]) == sid:
            found.append((layout.called(name) + f', which states `{name}`', entry))
        elif name in layout.others and sid in layout.homes(name):
            found.append((f'`{name}`, which this section writes into a proof', entry))
    if not found:
        return []
    lines = ['## Results of this section that a cited theorem contains', '',
             'Each result below is an instance of a general theorem of the literature. It follows from that theorem by '
             'the specialisation given with it, in a line or two. A session read the theorem in the source, at the '
             'place named, and wrote the specialisation down. A paper does not prove at length what a theorem it can '
             'cite contains, so the proof of such a result in this section is the citation and the specialisation. It '
             'cites the theorem at that place, says with which choice of the data of the theorem the result follows, '
             'and carries out whatever the specialisation leaves to be done. The longer proof in the record of the '
             'element is not written into the paper. A result that is a numbered statement is stated as the plan has '
             'it, in the form of its element and not in the general form of the source, and this short proof follows '
             'it. A result that the plan writes into a proof is taken from the theorem in the same way, at the place '
             'where that proof uses it. Write the specialisation in your own sentences and check each of its steps; '
             'what is given below is the argument, and it was not written as text for the paper.', '']
    for what, entry in found:
        lines += [f"- {what}: an instance of `\\cite[{collapsed(entry['where'])}]{{{entry['key']}}}`.", '',
                  '  The theorem states: ' + collapsed(entry['states']), '',
                  '  The specialisation: ' + collapsed(entry['specialisation']), '']
    return lines


def render_brief(materials, plan, section, layout=None, draft=None):
    """brief.md: what the session that writes or repairs one section works from, made from the plan and the materials.

    It holds the section's part of the plan and what of the plan every section needs; the records in
    full of the section's own elements, in dependence order; and, by their statements, the elements of
    other sections that those name, each with the place where the paper has it and the notation under
    which the paper knows it. With `draft`, the draft that the paper is written from, it also holds
    the statements and the formulas of the section as they were drafted (drafted_lines)."""
    layout = layout or Layout(materials, plan)
    sid, elements = section['id'], layout.elements
    full, cited = layout.full[sid], layout.cited[sid]
    lines = [f"# Brief for the section \"{section['title'].strip()}\"", '',
             f"Made by script, for the section whose id in the plan is `{sid}`, from the plan of the paper and from what "
             f"the proof of the root rests on, as the canon had it at revision {materials['revision']}. A name between "
             f"backquotes, such as `{materials['main']}`, is the name of a Lean declaration. It identifies an element here, "
             'in `plan.json` and in `elements/`, and it does not appear in the paper.', '',
             '## The paper', '', 'Title: ' + plan['title'].strip(), '',
             *([f"The main theorem of the paper is {layout.called(materials['main'])}, which states "
                f"`{materials['main']}`. The root of the research is settled by another element, "
                f"`{materials['settles']}`, which the paper states as {layout.called(materials['settles'])}. That "
                'statement is the one that says what the root says in words, in the conventions of the root as '
                '`root.md` gives it; the main theorem says what its own element says.', '']
               if 'settles' in materials else []),
             'How the proof goes and at which step its difficulty lies, in the words of the plan:', '',
             plan['outline'].strip(), '',
             'The sections in the order of the paper, each with its id and what the plan says it does. A section is '
             'referred to as `Section~\\ref{sec:<id>}`.', '']
    for number, other in enumerate(plan['sections'], 1):
        lines.append(f"{number}. `{other['id']}`, \"{other['title'].strip()}\"" + (' (this section)' if other['id'] == sid else '')
                     + ': ' + collapsed(other['content']))
    lines += ['', '## The notation', '']
    if plan.get('notation'):
        lines += ['The plan fixes these symbols and names for the whole paper. Every section uses them, and no others, '
                  'for these objects.', '']
        lines += [f"- {entry['symbol'].strip()}: {collapsed(entry['meaning'])}"
                  + (f" (the object of {backquoted(entry['elements'])})" if entry.get('elements') else '')
                  for entry in plan['notation']]
    else:
        lines.append('The plan fixes no notation.')
    lines += ['', '## The numbered statements of the paper', '',
              'All of them in the order of the paper: the kind and the label under which every section refers to the '
              'statement, the section that states it, what it is, and the element it states.', '']
    for item in plan['statements']:
        element, proof = elements[item['element']], layout.proof_of(item)
        lines.append(f"- {layout.called(item['element'])} · section `{item['section']}`"
                     + (' · cited, not proved' if proof == 'cited' else f' · proved in section `{proof}`'
                        if proof not in (None, item['section']) else '')
                     + f" · {element['short'] or shortened(element['description'] or '', 120)} · `{item['element']}`")
    lines += ['', '## What the plan puts into this section', '', collapsed(section['content']), '', *layout.assignment(sid), '',
              *display_lines(plan, section),
              *(drafted_lines(plan, section, draft)
                + instance_lines(section, draft, layout, materials['bibliography_keys']) if draft else []),
              '## The records in full', '',
              f'{len(full)} elements in dependence order: each comes after everything among them that it names. They are '
              'the elements that the plan puts into this section and, where the first line under a name says so, elements '
              'of other sections whose record this section needs whole.', '']
    for name in full:
        # Of a statement that this section states, the writer says what it is for: where the paper uses it.
        users = layout.used_elsewhere(name, sid) if name in layout.numbered and layout.numbered[name]['section'] == sid else []
        lines += [f'### `{name}`', '', ' '.join([layout.role(name, sid)] + layout.known_as(name)
                                              + (['Other sections use it in ' + ', in '.join(users) + '.'] if users else [])),
                  '', *element_lines(elements[name], users=False)]
    lines += ['## Elements of other sections, by their statements', '']
    if cited:
        lines += [f'The elements above name these {len(cited)} elements, which belong to other sections. Each is given by '
                  'what it says, with the place where the paper has it and, where the plan fixes one, the symbol or name '
                  'under which the paper knows it. A numbered one is referred to by its kind and its label. The full '
                  'record of each is in the file named with it.', '']
    else:
        lines += ['The elements above name no element of another section.', '']
    for name in cited:
        lines += [f'### `{name}`', '',
                  ' '.join([f'In the paper: {layout.placement(name)}.'] + layout.known_as(name)
                           + [f'Full record: `{layout.files[name]}`.']), '', *summary_lines(elements[name], users=False)]
    return '\n'.join(lines).rstrip('\n') + '\n'


def render_records(materials, plan, names, layout=None):
    """records.md for a comparison: the records in full of the elements `names`, and what their statements mention."""
    layout = layout or Layout(materials, plan)
    elements = layout.elements
    chosen = [name for name in elements if name in names]
    mentioned = [name for name in elements
                 if name not in names and any(name in elements[other]['mentions'] for other in chosen)]
    lines = ['# The records of the elements whose statements are compared', '', lean_names_note(materials), '',
             f'## The {len(chosen)} elements that the numbered statements of this section state, with their records in full', '']
    for name in chosen:
        lines += [f'### `{name}`', '', *layout.known_as(name), *([''] if name in layout.symbols else []),
                  *element_lines(elements[name])]
    lines += ['## What their statements mention', '']
    if mentioned:
        lines += ['Each is given by what it says, with the place where the paper has it and, where the plan fixes one, '
                  'the symbol or name under which the paper knows it. The full record of each is in the file named with it.', '']
    else:
        lines += ['Their statements mention no other element.', '']
    for name in mentioned:
        lines += [f'### `{name}`', '',
                  ' '.join([f'In the paper: {layout.placement(name)}.'] + layout.known_as(name)
                           + [f'Full record: `{layout.files[name]}`.']), '', *summary_lines(elements[name], users=False)]
    return '\n'.join(lines).rstrip('\n') + '\n'


def render_section_records(materials, plan, section, layout=None):
    """records.md for the comparison of the running text of one section: the records in full of the elements whose
    record the writer of the section had in full, and every other element of the materials by what it says."""
    layout = layout or Layout(materials, plan)
    elements, full = layout.elements, layout.full[section['id']]
    lines = [f"# The records for the section \"{section['title'].strip()}\"", '', lean_names_note(materials), '',
             f'## The {len(full)} elements whose records the writer of this section had in full', '',
             'The first line under a name says what the section does with the element.', '']
    for name in full:
        lines += [f'### `{name}`', '', ' '.join([layout.role(name, section['id'])] + layout.known_as(name)), '',
                  *element_lines(elements[name], users=False)]
    rest = [name for name in elements if name not in full]
    lines += ['## Every other element that the proof of the root rests on, by what it says', '',
              f'{len(rest)} elements. Each is given with the place where the paper has it and, where the plan fixes '
              'one, the symbol or name under which the paper knows it. The full record of each is in the file named '
              'with it.', '']
    for name in rest:
        lines += [f'### `{name}`', '',
                  ' '.join([f'In the paper: {layout.placement(name)}.'] + layout.known_as(name)
                           + [f'Full record: `{layout.files[name]}`.']), '', *summary_lines(elements[name], users=False)]
    return '\n'.join(lines).rstrip('\n') + '\n'


def running_text(plan, parts, spans):
    """What of each part the comparison of the running text is made on, by the id of the section it belongs to.

    The running text of a part is its text outside the numbered statements and outside the proof
    environments. It is given paragraph by paragraph, each with the lines of paper.tex it occupies; a
    paragraph that a statement or a proof interrupts is given in the pieces that stand outside them.
    Beside it stand the displayed formulas inside a proof that carry a label to which text outside that
    proof refers: such a formula is used as a result, so it is held to the elements as a statement is.
    The abstract is running text throughout, and it goes with the first section, as in a repair."""
    texts = {name: '\n'.join(part_lines(parts[name])) for name, _, _ in spans}
    first = {name: start for name, start, _ in spans}
    home = {'abstract': plan['sections'][0]['id'], **{section['id']: section['id'] for section in plan['sections']}}
    found = {section['id']: [] for section in plan['sections']}

    def span(a, b):
        return str(a) if a == b else f'{a} to {b}'

    for name, text in texts.items():
        proofs = [match.span() for match in PROOF_ENVIRONMENT.finditer(text)]
        # The characters of the statements and the proofs are blanked. A line on which nothing is left ends a
        # passage, as an empty line does.
        shown = list(text)
        for start, end in proofs + [match.span() for match in ENVIRONMENT.finditer(text)]:
            shown[start:end] = [char if char == '\n' else '\0' for char in text[start:end]]
        passage = []
        for index, line in enumerate(''.join(shown).split('\n') + ['']):
            visible = line.replace('\0', '').rstrip()
            if uncommented(visible).strip():
                passage.append((first[name] + index, visible))
            elif passage:
                found[home[name]].append({'kind': 'running text', 'part': name,
                                          'lines': span(passage[0][0], passage[-1][0]),
                                          'text': '\n'.join(visible for _, visible in passage)})
                passage = []
        for start, end in proofs:
            outside = ''.join(uncommented(other if other_name != name else other[:start] + other[end:])
                              for other_name, other in texts.items())
            referred = {target.strip() for match in REF.finditer(outside) for target in match[1].split(',')}
            for display in DISPLAY.finditer(text, start, end):
                labels = [label for label in LABEL.findall(display[0]) if label in referred]
                if labels:
                    found[home[name]].append({
                        'kind': 'formula of a proof, referred to from outside that proof', 'part': name,
                        'lines': span(first[name] + text.count('\n', 0, display.start()),
                                      first[name] + text.count('\n', 0, display.end())),
                        'labels': labels, 'text': display[0]})
    for entries in found.values():
        # The abstract first, then the section in the order of its lines.
        entries.sort(key=lambda entry: (entry['part'] != 'abstract', int(entry['lines'].split()[0])))
        for number, entry in enumerate(entries, 1):
            entry['entry'] = number
    return found


def named_part(plan, value):
    """The part that a reader names as the section of a finding, or None when it names none.

    A reader is asked for the label that follows the heading of the section, such as `sec:proof`, or
    for `abstract`. The id alone, the number of the section and its title are understood as well."""
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        return None
    text = collapsed(str(value))
    text = re.sub(r'^(?:section\s+|sec:)', '', text, flags=re.I).strip().lower()
    ids = [section['id'] for section in plan['sections']]
    if text == 'abstract' or text in ids:
        return text
    if text.isdigit():
        return ids[int(text) - 1] if 1 <= int(text) <= len(ids) else None
    titles = [collapsed(section['title']).lower() for section in plan['sections']]
    return ids[titles.index(text)] if text and titles.count(text) == 1 else None


# ----------------------------------------------------------------------------- the manuscript

def uncommented(text):
    return re.sub(r'(?<!\\)%.*', '', text)


TEX_SPECIAL = {'\\': r'\textbackslash{}', '{': r'\{', '}': r'\}', '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
               '_': r'\_', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}


def tex_plain(text):
    """A text that is no LaTeX, such as a name or an address of the title page, as LaTeX that prints it."""
    return ''.join(TEX_SPECIAL.get(char, char) for char in collapsed(text))


def read_title_page(path):
    """The authors that a title page file names: {"authors": [{"name", "address", "email"}]}; stops on another form."""
    try:
        page = json.loads(read_file(path))
    except (OSError, ValueError) as exc:
        raise Stop(f'the title page {path} cannot be read as JSON: {exc}')
    authors = page.get('authors') if isinstance(page, dict) else None
    if not isinstance(authors, list) or not all(
            isinstance(author, dict) and is_text(author.get('name'))
            and all(key not in author or is_text(author[key]) for key in ('address', 'email')) for author in authors):
        raise Stop(f'the title page {path} holds {{"authors": [...]}}, an array that may be empty; each author has a '
                   '"name" that is not empty and may have an "address" and an "email", each a text that is not empty')
    return [{key: author[key] for key in ('name', 'address', 'email') if key in author} for author in authors]


def read_classification(path):
    """The subject classification that a title page file gives under "msc2020": codes of the MSC 2020; stops on another form.

    The key is optional. The codes are not chosen by a session of this command: whoever runs it gives
    them, as the pipeline gives those that its selection chose for the registry."""
    try:
        page = json.loads(read_file(path))
    except (OSError, ValueError) as exc:
        raise Stop(f'the title page {path} cannot be read as JSON: {exc}')
    codes = page.get('msc2020', []) if isinstance(page, dict) else None
    if not isinstance(codes, list) or not all(isinstance(code, str) and MSC_CODE.fullmatch(code) for code in codes):
        raise Stop(f'the title page {path}: "msc2020", when it is given, is an array of codes of the Mathematics Subject '
                   'Classification 2020, such as 05A15')
    return list(codes)


def author_lines(authors):
    r"""The lines of the manuscript that name its authors, for amsart: \author, and \address and \email where given."""
    lines = []
    for author in authors:
        lines.append('\\author{' + tex_plain(author['name']) + '}')
        lines += ['\\' + key + '{' + tex_plain(author[key]) + '}' for key in ('address', 'email') if key in author]
    return lines


def assemble(plan, parts, authors=(), codes=()):
    """paper.tex from the parts, in the order of the plan, and the lines each part occupies in it.

    `authors` are the authors of the title page, each with a name and, where given, an address and
    an email. Without them the manuscript has no author line. `codes` are the codes of the subject
    classification, and the key words are those of the plan; amsart prints both at the foot of the
    first page, and a manuscript that is given neither has neither."""
    cites = any(CITE.search(uncommented(text)) for text in parts.values())
    title = plan['title'].strip()
    # Without an author, amsart takes the title for the running head of the even pages and puts it in capitals
    # a second time, the letters of its formulas included. The head is set here instead, on every page and
    # also when the title page names authors, from the short title when the plan gives one.
    lines = (PREAMBLE + '\\newcommand{\\RunningHead}{' + plan.get('short_title', title).strip()
             + '}\n\\uppercasenonmath\\RunningHead\n\\begin{document}\n\\title{' + title
             + '}\n' + ''.join(line + '\n' for line in author_lines(authors))
             + ('\\subjclass[2020]{' + ', '.join(codes) + '}\n' if codes else '')
             + ('\\keywords{' + ', '.join(word.strip() for word in plan['keywords']) + '}\n' if plan.get('keywords') else '')
             + '\\begin{abstract}').split('\n')
    spans = []

    def add(name):
        body = parts[name].strip('\n').split('\n')
        spans.append((name, len(lines) + 1, len(lines) + len(body)))
        lines.extend(body)

    add('abstract')
    lines += ['\\end{abstract}', '\\maketitle', RUNNING_HEAD]
    for section in plan['sections']:
        lines += ['', '\\section{' + section['title'].strip() + '}\\label{sec:' + section['id'] + '}']
        add(section['id'])
    if cites:
        lines += ['', '\\bibliographystyle{amsplain}', '\\bibliography{references}']
    lines += ['\\end{document}', '']
    return '\n'.join(lines), spans


TITLE_FIELD = re.compile(r'^\s*title\s*=\s*\{', re.M | re.I)


def capitals_kept(bibliography):
    """The bibliography for BibTeX, with the capitals of its titles kept where a TeX command writes them.

    A BibTeX style puts a title in lower case after its first letter and leaves alone what stands in
    braces. A group that begins with a command, as in {\\L}ukasiewicz or {\\'E}tale, is the exception:
    BibTeX reads it as one letter and lowers it with the rest, so that the name is printed with a small
    letter. A second pair of braces around such a group keeps the capital that the entry wrote."""
    out, position = [], 0
    for field in TITLE_FIELD.finditer(bibliography):
        index, depth = field.end(), 1  # just inside the braces of the field
        while index < len(bibliography) and depth:
            char = bibliography[index]
            if char == '{':
                depth += 1
                if depth == 2 and bibliography[index + 1:index + 2] == '\\':
                    end, inner = index + 1, 1
                    while end < len(bibliography) and inner:
                        inner += {'{': 1, '}': -1}.get(bibliography[end], 0)
                        end += 1
                    group = bibliography[index:end]
                    if not inner and re.search(r'[A-Z]', group):
                        out += [bibliography[position:index], '{', group, '}']
                        position = end
                    index, depth = end - 1, depth - 1 if not inner else depth
            elif char == '}':
                depth -= 1
            index += 1
    return ''.join(out) + bibliography[position:]


def found_statements(plan, parts):
    """The numbered statements in the parts, in the order of the paper, with the numbers TeX gives them."""
    found = []
    for number, section in enumerate(plan['sections'], 1):
        text = uncommented(parts.get(section['id'], ''))
        for count, match in enumerate(ENVIRONMENT.finditer(text), 1):
            label = LABEL.search(match[2])
            found.append({'label': label[1] if label else None, 'kind': match[1], 'section': section['id'],
                          'number': f'{number}.{count}', 'text': ' '.join(LABEL.sub('', match[2]).split()),
                          'proof_follows': bool(re.match(r'\s*\\begin\{proof\}', text[match.end():]))})
    return found


def cited_keys(text):
    r"""The keys of the bibliography that the \cite commands of a text name, in their order."""
    return [key.strip() for match in CITE.finditer(text) for key in match[1].split(',')]


def identifier_pattern(names):
    """Matches a Lean name of the canon: a full dotted name, or a last component that no ordinary word resembles."""
    words = set()
    for name in names:
        short = name.rsplit('.', 1)[-1]
        if '.' in name:
            words.add(name)
        if len(short) >= 5 and ('_' in short or re.search(r'[a-z0-9][A-Z]|[A-Za-z][0-9]', short)):
            words.add(short)
    if not words:
        return re.compile(r'(?!)')
    return re.compile(r'(?<![A-Za-z0-9_.\\])(?:' + '|'.join(re.escape(w) for w in sorted(words, key=len, reverse=True))
                      + r")(?![A-Za-z0-9_'])")


def machine_findings(materials, plan, parts, instances=()):
    """What a machine can check in the manuscript: each finding with the part in which it is to be corrected.

    A finding is {"part", "problem"}. "problem" is a sentence for a repair session. "part" is the name
    of a part, or None when the finding concerns no single part: the title, which the plan holds.
    `instances` are the numbered statements that the paper proves from a cited general theorem, each
    as (label, key of the bibliography, section that writes the proof) (Paper.instances)."""
    found_problems = []

    def bad(part, problem):
        found_problems.append({'part': part if part in parts else None, 'problem': problem})

    elements = {e['name']: e for e in materials['elements']}
    texts ={'the title': plan['title'], 'abstract': parts['abstract'], **{s['id']: parts[s['id']] for s in plan['sections']}}
    # Every numbered statement is one the plan names, of the planned kind, in the planned section and order.
    found = found_statements(plan, parts)
    planned = [(item['label'], item['kind'], item['section']) for item in plan['statements']]
    got = [(item['label'], item['kind'], item['section']) for item in found]
    for label, kind, section in planned:
        if (label, kind, section) not in got:
            bad(section, f'part {section}: the plan has a {kind} with \\label{{{label}}} here, and the part has none')
    for item in found:
        if (item['label'], item['kind'], item['section']) not in planned:
            bad(item['section'], f"part {item['section']}: the {item['kind']} numbered {item['number']} "
                + (f"with \\label{{{item['label']}}}" if item['label'] else 'without a \\label')
                + ' is not a numbered statement of the plan; every numbered statement states an element the plan names')
    # A statement without a \label has the label None, which cannot be ordered beside a text; repr can.
    if sorted(got, key=repr) == sorted(planned, key=repr) and got != planned:
        for section in plan['sections']:
            here = [label for label, _, sid in planned if sid == section['id']]
            if here != [label for label, _, sid in got if sid == section['id']]:
                bad(section['id'], f"part {section['id']}: the numbered statements are not in the order of the plan: "
                    + ', '.join(here))
    by_label = {item['label']: item for item in found}
    for item in plan['statements']:
        # A statement is followed by its proof, or proved in the section the plan names, or cited and not proved.
        element, label, here = elements[item['element']], item['label'], by_label.get(item['label'])
        proof = item.get('proof', item['section']) if element['kind'] == 'statement' else None
        if here is None or proof is None:
            continue
        if proof == 'cited':
            if element['source'] not in cited_keys(here['text']):
                bad(item['section'], f"part {item['section']}: {label} is a result from the literature; its statement "
                    f"carries \\cite{{{element['source']}}}")
            if here['proof_follows']:
                bad(item['section'], f"part {item['section']}: {label} is a result from the literature; it is cited and "
                    'has no proof')
        elif proof == item['section']:
            if not here['proof_follows']:
                bad(proof, f"part {proof}: the proof of {label} follows its statement directly, in a proof environment")
        elif not re.search(r'\\begin\{proof\}\[[^\]]*\\ref\{' + re.escape(label) + r'\}', uncommented(parts[proof])):
            bad(proof, f"part {proof}: the plan puts the proof of {label} here; it opens with "
                f"\\begin{{proof}}[Proof of ...~\\ref{{{label}}}]")
    for item in plan['others']:
        key = elements[item['element']]['source']
        if item['treatment'] == 'cited' and key not in cited_keys(uncommented(parts[item['section']])):
            bad(item['section'], f"part {item['section']}: the plan cites the result with the bibliography key {key} "
                'here, and the part does not')
    # A formula that several sections use is displayed by the section the plan names, under the plan's label.
    for entry in plan.get('displays') or []:
        if '\\label{' + entry['label'] + '}' not in uncommented(parts[entry['section']]):
            bad(entry['section'], f"part {entry['section']}: the plan has this section display a formula to which the "
                'sections ' + ', '.join(entry['used_in']) + f" refer, with \\label{{{entry['label']}}}, and the part has "
                'no such label: ' + shortened(entry['formula'], 200))
    # A statement that the draft found to be an instance of a cited theorem is proved by that citation.
    for label, key, proof in instances:
        if key not in cited_keys(uncommented(parts[proof])):
            bad(proof, f"part {proof}: the proof of {label} takes the result from a theorem of the literature, by the "
                f"specialisation that the brief gives; it carries \\cite{{{key}}}")
    # Labels and citations resolve. A label the plan gives to a section is that section's: when it is defined twice
    # the other part gives it up, and when it is missing the part that owes it is the one to correct.
    owner = {**{item['label']: item['section'] for item in plan['statements']},
             **{entry['label']: entry['section'] for entry in plan.get('displays') or []}}
    defined = [(name, m[1]) for name, text in texts.items() for m in LABEL.finditer(uncommented(text))]
    labels = ['sec:' + s['id'] for s in plan['sections']] + [label for _, label in defined]
    for label in sorted({label for label in labels if labels.count(label) > 1}):
        places = [name for name, other in defined if other == label]
        keeper = owner.get(label, None if label.startswith('sec:') else places[0])
        for name in dict.fromkeys(places):
            if name != keeper or places.count(name) > 1:
                bad(name, f'{name}: \\label{{{label}}} is defined more than once'
                    + (f', here and in {keeper}; this part takes another label' if name != keeper and keeper else ''))
    keys = set(materials['bibliography_keys'])
    for name, text in texts.items():
        plain = uncommented(text)
        for target in sorted({m[1] for m in REF.finditer(plain)} - set(labels)):
            bad(owner.get(target, name), f'{name}: \\ref{{{target}}} points to a label that the manuscript does not define')
        for key in sorted(set(cited_keys(plain)) - keys):
            bad(name, f'{name}: \\cite{{{key}}} is not a key of the bibliography; only works in the bibliography of the '
                'materials are cited')
        commands = sorted({m[1] for m in FORBIDDEN.finditer(plain)})
        if commands and name != 'the title':
            bad(name, f'{name}: a part does not use ' + ', '.join('\\' + c for c in commands) + '; the script supplies the '
                'preamble, the title, the section headings and the bibliography')
        strange = sorted({c for c in text if ord(c) > 127})
        if strange:
            bad(name, f'{name}: the manuscript is written in ASCII; write these characters as LaTeX: ' + ' '.join(strange))
    if REF.search(uncommented(parts['abstract'])) or CITE.search(uncommented(parts['abstract'])):
        bad('abstract', 'abstract: the abstract stands by itself, without \\ref and without \\cite')
    # The paper names no declaration or module of the canon and does not mention Lean, anywhere in a part, comments
    # and labels included. Only the words are looked for; another way of speaking of a formal proof is not.
    pattern = identifier_pattern(materials['identifiers'])
    where = ' (method, section "The implementation does not show")'
    for name, text in texts.items():
        plain = text.replace('\\_', '_')
        names = sorted({m[0] for m in pattern.finditer(plain)})
        if names:
            bad(name, f'{name}: Lean names of the canon appear: ' + ', '.join(names) + '; the paper calls an object by its '
                'mathematical name' + where)
        words = sorted({m[0] for m in LEAN_WORDS.finditer(plain)})
        if words:
            bad(name, f'{name}: the paper does not mention Lean, and this part has the words ' + ', '.join(words) + where)
    return found_problems


# ----------------------------------------------------------------------------- typesetting

def tex_recipe(command):
    """The command lines that typeset paper.tex in its folder, or None when no TeX command is available."""
    if not command:
        command = next(([path] for path in map(shutil.which, ENGINES) if path), None)
        if command is None:
            return None
    elif shutil.which(command[0]) is None:
        raise Stop(f'the TeX command {command[0]} was not found')
    engine = Path(command[0]).stem.lower() if len(command) == 1 else None
    if engine == 'tectonic':
        return [[command[0], '--keep-logs', 'paper.tex']]
    if engine == 'latexmk':
        return [[command[0], '-pdf', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error', 'paper.tex']]
    if engine == 'pdflatex':
        run = [command[0], '-interaction=nonstopmode', '-halt-on-error', '-file-line-error', 'paper.tex']
        path = Path(command[0])
        bibtex = str(path.with_name('bibtex' + path.suffix)) if path.parent != Path('.') else 'bibtex'
        return [run, [bibtex, 'paper'], run, run]
    return [[*command, 'paper.tex']]


def remove_pdf(folder):
    """Take paper.pdf out of a folder, so that a PDF there is always one of the manuscript beside it.

    Windows does not remove a file that another program has open, and a viewer keeps a PDF open while it shows
    it. The command cannot free the file, so it stops and says what does."""
    path = Path(folder) / 'paper.pdf'
    try:
        path.unlink(missing_ok=True)
    except PermissionError as exc:
        raise Stop(f'{path} cannot be removed ({exc}). On Windows that is so while another program has the file open, '
                   'as a viewer has while it shows the paper. Close the file there and give the command again: '
                   '--resume continues a run that was stopped, and --typeset-only typesets a finished manuscript')


def typeset(folder, recipe):
    """Run the TeX commands in the folder; returns the errors of the run, or nothing when paper.pdf was made.

    A command that does not finish within TEX_SECONDS stops the run, as one that cannot be started does, and so
    does one that does not find a file of the TeX installation (MISSING_FILE): it reports no error that a change
    of a part would answer, so it is not handed to a repair session."""
    folder = Path(folder)
    remove_pdf(folder)
    cites = bool(CITE.search(uncommented(read_file(folder / 'paper.tex'))))
    for command in recipe:
        bibtex = Path(command[0]).stem.lower() == 'bibtex'
        if bibtex and not cites:
            continue  # BibTeX fails on a paper that cites nothing
        try:
            done = subprocess.run(command, cwd=folder, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, timeout=TEX_SECONDS, **popen_options())
        except subprocess.TimeoutExpired:
            raise Stop(f'{command[0]} did not finish within {TEX_SECONDS} seconds. No part of the manuscript is known '
                       'to cause that, so it goes to no repair session. See why the TeX command takes this long, as '
                       'it can when it fetches its files at its first run, and give the command again: --resume '
                       'continues a run that was stopped, and --typeset-only typesets a finished manuscript')
        except OSError as exc:
            raise Stop(f'{command[0]} could not be started: {exc}')
        output = done.stdout.decode('utf-8', errors='replace').replace('\r\n', '\n')
        with (folder / 'typeset.log').open('a', encoding='utf-8', newline='\n') as stream:
            stream.write('$ ' + ' '.join(command) + '\n' + output + '\n')
        if done.returncode and not (bibtex and done.returncode == 1):  # BibTeX returns 1 for warnings
            log = folder / 'paper.log'
            text = (log.read_text(encoding='utf-8', errors='replace') if log.is_file() else '') + '\n' + output
            lacking = MISSING_FILE.search(text)
            if lacking:
                raise Stop(f'{command[0]} did not find a file of the TeX installation: {lacking[0]}. The class, the '
                           'packages and the bibliography style are those of the preamble that the script supplies, '
                           'and a part names no such file, so no part of the manuscript causes this and it goes to no '
                           'repair session. Install what is missing, or give another TeX command, and give the command '
                           'again: --resume continues a run that was stopped, and --typeset-only typesets a finished '
                           'manuscript')
            lines = text.splitlines()
            starts = [i for i, line in enumerate(lines) if line.startswith('!') or re.match(r'\S*:\d+: ', line)
                      or 'error:' in line.lower()][:10]
            errors = ['\n'.join(lines[i:i + 5]) for i in starts] or ['\n'.join(lines[-30:])]
            return [f"{' '.join(command)} ended with exit code {done.returncode}", *errors]
    if not (folder / 'paper.pdf').is_file():
        return ['the TeX command ended without an error and left no paper.pdf']
    return []


# Where TeX opens the bibliography. Its log names the file as `(paper.bbl` or `(./paper.bbl`, and it breaks a line
# after 79 characters, also inside a name, so a line end may stand anywhere in this one.
BIBLIOGRAPHY_OPENED = re.compile(r'\((?:\.\n?/\n?)?' + r'\n?'.join(re.escape(char) for char in 'paper.bbl'))


def wide_lines(log):
    """The lines that TeX set wider than the text block by more than WIDE_PT, as its log reports them.

    TeX reports such a line as a warning and typesets the paper all the same, with the line standing
    out into the margin. It gives the line by its number in the file it is reading. That file is
    paper.tex up to the bibliography, which is the last thing in the manuscript and which TeX reads
    from paper.bbl. A number that the log gives from there on is therefore no line of paper.tex, and
    such a line is reported without one: it stands in the bibliography, or in the addresses that the
    class prints below it."""
    log = Path(log)
    if not log.is_file():
        return []
    text = log.read_text(encoding='utf-8', errors='replace')
    opened = BIBLIOGRAPHY_OPENED.search(text)
    body, rest = (text[:opened.start()], text[opened.start():]) if opened else (text, '')
    found = []
    for width, single, first, last in OVERFULL.findall(body):
        if float(width) > WIDE_PT:
            where = f'line {single}' if single else f'lines {first} to {last}'
            found.append(f'paper.tex, {where}: TeX set a line {float(width):.0f}pt wider than the text block')
    found += [f'the bibliography, or the addresses below it: TeX set a line {float(width):.0f}pt wider than the text block'
              for width, _, _, _ in OVERFULL.findall(rest) if float(width) > WIDE_PT]
    return list(dict.fromkeys(found))


# A displayed formula that is too long for its line does not always stand out into the margin. TeX first closes
# up the spaces around its + and - signs, and when the formula has a number it moves the number to a line of its
# own; neither is an "Overfull" line of the log. So the manuscript is typeset a second time, only to be measured:
# with these lines in its preamble a display cannot close up its spaces, and a numbered `equation` has the width
# of its line less the room of its number, which is then left out. What TeX then reports as too wide is a display
# that has less room than it needs. The PDF of this typesetting is not used.
DISPLAY_ROOM = (r'\makeatletter\everydisplay\expandafter{\the\everydisplay\medmuskip=4mu plus 2mu\relax}'
                r'\let\paper@equation\equation\def\equation{\paper@equation'
                r'\setbox\z@\hbox{\maketag@@@{(\theequation)}}'
                r'\advance\displaywidth-\dimexpr\wd\z@+\fontdimen6\textfont2\relax\def\maketag@@@##1{}}\makeatother')
TIGHT = re.compile(r'Overfull \\hbox \(([0-9.]+)pt too wide\) detected at line (\d+)')


def tight_displays(folder, recipe):
    """The displayed formulas of the typeset manuscript in `folder` that have less room than they need.

    Each is given by the line of paper.tex at which it ends. A display that the log of the manuscript itself
    reports as too wide is left to `wide_lines`. When the second typesetting fails or does not finish, nothing is
    reported: the manuscript itself was typeset, and this measurement adds to that and decides nothing about it."""
    folder = Path(folder)
    measured = folder / 'displays'
    measured.mkdir(exist_ok=True)
    write_text(measured / 'paper.tex',
               read_file(folder / 'paper.tex').replace('\\begin{document}', DISPLAY_ROOM + '\\begin{document}', 1))
    if (folder / 'references.bib').is_file():
        shutil.copyfile(folder / 'references.bib', measured / 'references.bib')
    try:
        if typeset(measured, recipe):
            return []
    except Stop:  # the TeX command did not finish in its time
        return []
    logs = [path.read_text(encoding='utf-8', errors='replace') if path.is_file() else ''
            for path in (folder / 'paper.log', measured / 'paper.log')]
    known = {line for _, line in TIGHT.findall(logs[0])}
    found = {}
    for width, line in TIGHT.findall(logs[1]):
        if float(width) > WIDE_PT and line not in known:
            found[line] = max(found.get(line, 0.0), float(width))
    return [f'paper.tex, line {line}: the displayed formula that ends here is {width:.0f}pt wider than the room it has '
            'on its line (beside its number, when it has one), so TeX closed up the spaces in it or moved its number to '
            'a line of its own' for line, width in sorted(found.items(), key=lambda item: int(item[0]))]


WIDE_LINE = re.compile(r'paper\.tex, lines? (\d+)')


def part_at(spans, line):
    """The part whose text holds a line of paper.tex, or None for a line that the script supplied."""
    return next((name for name, first, last in spans if first <= line <= last), None)


# ----------------------------------------------------------------------------- prompts

CONTEXT = '''A script is turning a finished piece of mathematical research into a paper. The research is a Lean library, \
called the canon, whose main statement, the root, has been settled by a formal proof; every declaration of the library is \
an element, and beside it is a written record. The script launches AI sessions, some of them side by side, and each does \
one part of the work. No session can ask another what it meant, and nobody answers questions while the script runs.'''

# The entry of the method in the prompt of a session that plans, sketches, writes, repairs or resolves. The last two
# sections of the method describe what the script gives each session and what the script and other sessions do after
# the writing. No session receives them (method_before_checks), and each prompt carries what of them concerns its
# session. The section before them, the last of the file, instructs the sessions that read the manuscript beside real
# papers, and the prompts of a repair and of the resolving session, which take up what they found, name it.
METHOD_BEFORE_CHECKS = '''- `paper-method.md` is the method that every session follows, here without its last two \
sections, "What each session works from" and "What is checked after writing", which other sections name. They say \
what the script gives each session, and what the script and other sessions do with the manuscript once it is written; \
what of them concerns this session is in this prompt. Read the file in full before anything else, except its last \
section here, "Reading the manuscript beside real papers": it instructs the sessions that read the manuscript beside \
real papers, and you read it when this prompt names it.'''

PREFERENCES_FILE = '''- `user-writing-preferences.md` describes the writing that the person who will read the paper first \
prefers, with the occasions on which the preferences came to light. The method says how it bears on a paper.'''

# The prompt of the planning session is made of the pieces below. The session that repairs the plan of a draft and
# the session that resolves what the readings left open are given the keys of a plan and the conditions under which
# the script accepts one in the same words.
PLAN_OPENING = CONTEXT + '''

This session plans the paper. The sessions after it write the sections from the plan, side by side and without seeing \
each other's text, and the script holds the manuscript to the plan.

In this folder:
''' + METHOD_BEFORE_CHECKS + '''
- `materials-digest.md` is a digest of everything the proof of the root rests on. With the files of the next entry it is \
the only source of the mathematics and of the literature. Read it in full.
- `elements/` holds the full record of every element, one file each; the digest names the file at each element. The \
digest leaves the explanations and the proofs to these files so that the whole proof can be planned in one reading, and \
nothing is withheld by that. Open the file of an element whenever a decision needs what the digest leaves out: whether a \
step is routine or carries an idea, how long an argument is, which elements belong to one idea, what a source in the \
literature was read for.
''' + PREFERENCES_FILE + '''
- `exemplars.md` lists the collection of research articles that the method's section "The papers this paper is written \
like" describes, with the field, the length and the abstract of each paper and why it is in the collection. Each of them \
is in `exemplars/<key>.tex`, as the LaTeX source that its authors wrote.

The papers come first. From `exemplars.md` choose the ''' + str(CHOSEN_PAPERS) + ''' papers that this paper is to be \
written like, those from which the most can be learned for it, as that section says: near it in subject, near it in \
length. You may look into a paper's file before you choose it. Then read each of the chosen papers whole, from the title \
to the references, for how it is written and not for what it proves, in the way that section describes. Plan the paper \
after that reading and in its light. A session that writes or repairs a section receives your account of the reading and \
reads whole the ''' + str(SECTION_PAPERS) + ''' of your papers that you name for its section.

Write `output/plan.json`: a JSON object with the keys below. A value that will be printed (the title, a section \
title, a symbol) is LaTeX; inside a JSON string a backslash is written twice.

'''
PLAN_KEYS = '''- "exemplars": the keys of the ''' + str(CHOSEN_PAPERS) + ''' papers you chose, all different, exactly as \
`exemplars.md` gives them.
- "title": the title of the paper. Like the parts of the manuscript it is plain ASCII, and so are "short_title" and \
the "title" of every section: a letter with an accent is written with TeX's accent command.
- "short_title": the title in a shorter form, for the running head. The head is one line of small capitals at the top \
of every page, beside the page number, and it has room for about fifty-five letters and spaces. Leave the key out when \
the title itself is no longer than that. A head that does not fit is not printed, and the pages then carry their \
numbers alone.
- "keywords": a few key words and phrases under which a reader of the field would look for this paper, as an array of \
texts in ASCII. The script prints them at the foot of the first page, where a research article has them.
- "outline": a few sentences for the writers saying how the proof goes and at which step its difficulty lies. The outline \
of the proof in the introduction, and the room each proof receives, follow it.
- "sections": the sections in the order of the paper, each {"id", "title", "content", "exemplars"}. "id" is a short \
lowercase word ([a-z][a-z0-9-]*) that names the section in file names and labels. "content" says in a sentence or two \
what the section does and what it contains. "exemplars" are the keys of ''' + str(SECTION_PAPERS) + ''' of your \
''' + str(CHOSEN_PAPERS) + ''' papers: those from which the most can be learned for a section of this kind, for example \
the ones whose introductions do what this introduction has to do, or whose sections carry a computation of this sort. \
The first section is the introduction. The abstract and the list of references are not sections.
- "statements": the numbered statements in the order in which the paper has them, each {"element", "kind", "label", \
"section", "proof", "reason"}. "element" is the name of the element it states, exactly as the materials give it. "kind" is \
theorem, proposition, lemma, corollary or definition. "label" is its LaTeX label: a prefix, a colon and a lowercase word \
for the mathematics, such as "thm:main" or "lem:step"; it never contains the name of the element. "section" is the id of \
the section that states it. "proof" is the id of the section where its proof is written; leave it out when the proof \
follows the statement, and for a definition. For a result taken from the literature "proof" is "cited": the statement \
carries its citation and is not proved. "reason" is needed when an element whose weight is step is numbered.
- "others": every other element of the materials, each {"element", "treatment", "reason"} with one more key that depends \
on the treatment. "absorbed" has "into": the names of the numbered elements into whose proofs it is written (for a \
definition, also whose statements), or the ids of the sections in whose running text it is given. "cited" has "section": \
the id of the section whose running text cites this result from the literature. "not_stated" has "by": the element that \
stands in its place in the paper. "reason" is a sentence; it is needed when a unit is not numbered and whenever an element \
is not stated.
- "notation": the symbols and names of the paper, each {"symbol", "meaning", "elements"}. "symbol" is the symbol, or the \
name in words of an object that has no symbol. "meaning" says exactly what it denotes, with its conventions: where an \
index starts, how a quantity is normalised. "elements" are the names of the definitions of the materials whose object \
the entry denotes. It names several where the canon spreads one mathematical object over several declarations, it is \
empty for an entry that denotes no element, and a definition is named in one entry only. The method's section "What \
holds the sections together" says which objects receive an entry, and why.
- "displays": the displayed formulas that more than one section needs, each {"label", "section", "element", "formula", \
"used_in"}; an empty array when there is none. The sections are written side by side, and a writer cannot refer to a \
formula that another writer numbers, because nothing tells the first that it will be there. A formula that two \
sections need is then displayed twice, under two numbers, which happens often. \
The plan prevents this by giving the formula one place. "section" is the id of the section that displays it: the first \
of the sections that need it, in the order of the paper. "label" is the label under which every section refers to it; \
it begins with `eq:`, the id of that section and a hyphen, as in "eq:tools-recursion". "element" is the name of the \
element that states the formula, which may be a step that the plan absorbs there or a definition; a formula that no \
element states cannot be used as a result by another section, as the method's section "What the running text asserts" \
says. "formula" is the formula in LaTeX, in the notation of the plan, so that every section speaks of the same one. \
"used_in" are the ids of the later sections that refer to it. List a formula when the materials show that two sections \
will need it displayed: a recursion that one section derives and a later one applies, a bound that several proofs in \
different sections quote. What an element states as a whole is better given a number, since every section can refer \
to a numbered statement already.
'''
# One more key, which only the plan of a draft is asked for (--draft): the results the paper would cite.
PLAN_CITATIONS = '''- "citations": the results that this paper would cite and not prove if their records named a \
source, each {"element", "result", "reason"}; an empty array when there is none. The method's section "Results from the \
literature" says that a result which the literature already has is cited in the paper and not proved again, and the \
script lets a plan cite only an element whose record names a source. Some elements state such a result all the same: a \
classical identity, a standard inequality, a theorem that carries a name, which the research proved for itself and \
recorded without a source. You recognise them where a mathematician of the field would say that the result is known \
and where it is found. "element" is the name of such an element, a statement whose record names no source. "result" is \
the name under which the result is known, with its author where it has one, as exactly as you can give it, because a \
later session searches the literature for it under that name. "reason" says in a sentence why the paper should cite it \
and not prove it. In this plan such an element is still treated like every other element without a source, that is, \
numbered or absorbed with its proof, because the script accepts nothing else. After this run a session looks for a \
source of each listed result and enters it into the record only where it finds a work that states the result in the \
form the element has; the script then changes the plan to cite it. So list a result when you are confident that the \
literature has it in that form, and do not list a result that this research found, however natural it looks.
'''
PLAN_ACCEPTS = '''
The script accepts the plan when every element of the materials appears in it exactly once; when kinds, labels, sections \
and reasons have the form above; when the main result is a theorem stated in the first section before every other \
theorem, proposition, lemma and corollary; when no statement mentions an object that is defined in a later numbered \
definition, and no proof comes before a numbered statement it rests on; when an element absorbed into a numbered \
statement is one that statement or its proof rests on; when only results with a source in the literature are cited; \
when an element that is not stated has in its place an element its proof names, another proof of the same statement, or \
the definition it is stated to agree with; when "exemplars" names ''' + str(CHOSEN_PAPERS) + ''' different keys \
of `exemplars.md` and every section names ''' + str(SECTION_PAPERS) + ''' different ones of them; when every entry \
of "displays" names an element of the materials, a section, later sections that use the formula, and a label that \
begins with `eq:` and the id of its section; and when every \
definition of the materials that the writers of two sections meet, because their elements state it, absorb it, name it \
or mention it, is named in "elements" of an entry of "notation". That last check sees only the definitions of the \
materials; for every other object the notation rests on your reading.'''
PLAN_CLOSING = ''' A plan that fails goes to a new planning session with the list of failures.

Write also `output/study.md`: your account of how the chosen papers are written, as the method's section "The papers \
this paper is written like" describes it, in free text.

Use no source other than the files in this folder. Write no part of the paper itself.
'''

BRIEF_FILE ='''- `brief.md` is what this section {tense} written from. The script made it from the plan and from the records of \
the research. It is the source of the mathematics of this section. Read it in full.'''

RESEARCH_FILES = '''- `root.md` holds the root in words and in Lean, the record of the root, and the account of the \
problem as a whole that the research kept. {root}
- `elements/` holds the full record of every element that the proof of the root rests on, one file each, and \
`elements.md` lists the elements with their files. {elements}
- `references.bib` is the bibliography of the research. The paper cites works that are in it, by their keys, and no \
others.'''
ROOT_FIRST = 'The introduction is written from it: read it in full.'
ROOT_LATER = ('The paper uses the conventions of the root as it is stated in words: read that statement. The rest is '
              'there for when you need more of the whole than the outline in your brief gives.')
ELEMENTS_SECTION = ('Your brief gives an element of another section by what it says: you use a result of another section '
                    'by its statement and do not need its proof, as an author does who cites a lemma. Where that is not '
                    'enough, for example because a proof of this section needs to know how such an element is proved, '
                    'open its file. `plan.json` is the whole plan, for a question about another section that the brief '
                    'does not answer.')
ELEMENTS_WHOLE = ('`plan.json` says which element each numbered statement states and into which statements the other '
                  'elements are written. Open the records of the elements whose text you change. One kind of proof is '
                  'not rewritten from its record: where the manuscript proves a result by citing a general theorem and '
                  'giving the specialisation, the proof keeps that form (method, section "Results from the '
                  'literature"), and the longer proof in the record is not written into the paper.')

STUDY_FILE = '''- `study.md` is the planning session's account of how the papers it chose for this paper are written, part \
by part, made so that sessions which do not see each other write from one reading of the same papers.'''

WRITE_PROMPT = CONTEXT + '''

This session writes one section of the paper: "{title}", whose id in the plan is `{id}`.{also}

The sections are written by sessions that do not see each other at work. {order} What makes one paper of the sections is \
the plan, which an earlier session made and the script checked.

In this folder:
''' + METHOD_BEFORE_CHECKS + '''
''' + BRIEF_FILE.format(tense='is') + ''' Follow the plan as the brief gives it: the same numbered statements with the same \
kinds and labels in the same order, the same treatment of every element, the same notation.{drafted}
''' + RESEARCH_FILES + '''
''' + PREFERENCES_FILE + '''
{parts}
''' + STUDY_FILE + '''
- `exemplars/` holds {count} of those papers, {papers}, each as the LaTeX source that its authors wrote. The plan names \
them for this section as the ones from which the most can be learned for a section of this kind. The method's section \
"The papers this paper is written like" says what the papers are for.

What the plan gives this section: {content}

The papers come before the writing. Read `study.md`, and read the papers in `exemplars/` whole, from the title to the \
references, for how they are written and not for what they prove, as that section of the method describes; look above \
all at the places where the papers do what this section does. Then write the section as those papers are written, with \
the mathematics and the wording of the statements from the brief.

Your section has to stand whatever the writers of the other sections write, so it rests on the plan alone:

- Refer to another section as `Section~\\ref{{sec:<id>}}`, and to a result or a definition of another section by its \
numbered statement, as in `Lemma~\\ref{{<label>}}`, with the ids and the labels of the brief. These exist whoever writes \
the other sections. An equation, a subsection or a remark of another section cannot be referred to, also where you see \
one in `parts/`: a repair of that section may remove it. The one exception is a formula that the brief lists under \
"Displayed formulas that several sections use", when the brief has that heading: the plan fixes the label of such a \
formula and the section that displays it.
- An object that the plan does not name is yours to name: introduce its notation inside your section, where it is \
first used, and do not rely on another section having introduced it.
- An element of another section that has no number cannot be referred to. The brief says so at the element, and it gives \
the record in full where a proof of this section may use it: its content is then written at the place of use. An object \
that another section defines in its running text is used here under the notation of the plan and is not defined a \
second time; a reference to that section tells the reader where the definition is.
- Begin every label that you create with `eq:{id}-` for an equation and with `subsec:{id}-` for a subsection, so that no \
two sections create the same label.

Write `output/{id}.tex`: the body of the section in LaTeX, beginning after the section heading, which the script \
supplies.{abstract} The method's section "The LaTeX of a part" says what the script supplies and what a part contains.

The script checks afterwards that the numbered statements of your part are those of the plan, that every \\ref and \\cite \
resolves, that your part contains no Lean name of the canon and neither of the words Lean and Mathlib, its comments \
and labels included, and that TeX typesets the whole. Later sessions compare each numbered statement with its element, \
and the text outside the statements and the proofs with the records: a sentence there that asserts mathematics which no \
element states is cut or reworded, as the method's section "What the running text asserts" describes. That section \
also says where a derivation belongs that a proof uses: inside that proof, at the place where the proof uses it. Before \
you finish, read your part from its first line as the reader of the method would, and correct what that reader could not \
follow. Use no source other than the files in this folder.
'''
# What the writer of a section is told when the paper is written from a draft (--from-draft).
DRAFTED = (' Under "The statements and formulas of this section as they were drafted" the brief also gives texts of '
           'this section that an earlier session drafted. They stand in your section as they are drafted there, for the '
           'reason the brief gives at that place.')
ORDER_FIRST = ('The introduction, which is this section, is written first and alone; the other sections are written after '
               'it, side by side, and their writers receive it.')
ORDER_AGAIN = ('The introduction, which is this section, is written alone; the sections in `parts/` were written by an '
               'earlier run of the script, without it.')
ORDER_LATER = 'The introduction was written first; the other sections, of which this is one, are written side by side.'
NO_PARTS = '- No section was finished when this session started, so this folder has no `parts/`.'
PARTS = ('- `parts/` holds the parts that were finished when this session started, as the paper carries them unless a '
         'repair changes them: {held}.{others} Consult them for how the paper speaks of its objects and in which voice. '
         'Your section does not repeat what they say.')
PARTS_OTHERS = (' The other sections are written while this session runs or after it, and you do not see them, whether '
                'they come before yours in the paper or after it.')

RESPONSE = ''' Write also `output/response.json`: an array with one object for each entry of the findings, in their \
order, {"finding": <its number, from 1>, "action": "revised" or "kept", "note": "<what you changed, or why the text stays>"}; \
an empty array when there is no finding.'''

# What a repair session is told about its findings: for a session that repairs one section, and for the session that
# takes up what concerns no single section and may change every part. Each text says first what the findings are and
# then what the session does with them; a narrow repair is told the first in the same words and the second otherwise.
READ_SECTION = '''A session that had the manuscript and nothing else read it as the reader the method describes. \
`findings.json` holds, under "findings", the places in this section where that reader could not follow, missed something, \
found an error, or met text that does not belong in a paper. Under "understanding" it holds what the reader took the whole \
paper to prove and how, so that you see how the paper was read{compared}.'''
READ_DECIDE = '''Decide for each finding whether the manuscript has to change. A reader can misread, and a finding can ask \
for something the method excludes; in that case keep the text and say why.'''
READ_ELSEWHERE = ''' So do you when the cause of a finding lies in another \
section, which this session does not change: say in the note which section, and what would have to change there.'''
READ_WHOLE = '''A session that had the manuscript and nothing else read it as the reader the method describes. \
`findings.json` holds its report: "understanding" is what that reader took the paper to prove and how; "findings" are the \
places where the reader could not follow, missed something, found an error, or met text that does not belong in a paper, \
as far as they concern no single section. What the reader found in one section has gone to a session that repaired that \
section, and `paper.tex` is the manuscript as those sessions left it.'''
COMPARED_SECTION = '''A session compared the numbered statements of this section with the statements of their elements. \
`findings.json` lists the statements it found to differ. A numbered statement says exactly what its element says \
(method, section "Every numbered statement says what its element says"). Correct each statement that differs, and adjust \
its proof and the places of this section that use it where the correction requires it. When a reported difference is one \
the method permits, keep the statement and say why. The proof of a statement, or a use of it, can stand in another \
section, which this session does not change. The writer of that section worked from the statement of the element, as \
your brief gives it, and not from the wording that you now correct; where the correction nevertheless requires a change \
there, say in the note which section and what.'''
LIKE_FOUND = '''A session that had the manuscript and four research articles from refereed journals, and nothing \
else, read the manuscript beside those papers, as the method's section "Reading the manuscript beside real papers" \
describes. `findings.json` holds what it found{scope}: places where the manuscript is written otherwise than real \
papers are written. Each finding gives the place ("where"), the passage of the manuscript ("quote", empty when the \
finding is that something is missing), passages from those papers that show what they do at such a place \
("evidence"), and the difference ("difference").'''
LIKE_SECTION, LIKE_WHOLE = (LIKE_FOUND.format(scope=scope)
                            for scope in (' in this section', ', as far as it concerns no single section'))
LIKE_KEPT = '''The mathematics stays as it is, and so do the plan and the decisions of the method; the passages show \
manner, and no sentence of theirs is copied or paraphrased into the manuscript. Where following a finding would change \
the mathematics, depart from the plan or undo a decision of the method, such as that the author line is the script's to \
write or that the paper does not mention Lean, keep the text and say why.'''
# What the repair of a sentence that no element covers is told about its findings. The repair is always a narrow one.
COVERED_FINDINGS = '''A session compared the running text of this section with the elements of the research, that is, the text \
outside the numbered statements and outside the proofs, together with the displayed formulas of a proof to which text \
outside that proof refers. `findings.json` lists the passages that it found to assert mathematics which no element \
states. Each finding gives the place ("where"), the exact words ("quote"), what the passage asserts ("asserts"), the \
element whose statement comes nearest to it ("nearest", whose record is in `elements/`), and what the passage asserts \
beyond that element ("difference"). A finding can have "source" in the place of "nearest". It then concerns a \
sentence that says something of a cited work, and "source" is the key of that work in the bibliography. \
`attributions.json`, which is in this folder whenever there is such a finding, holds the words of the cited works at \
the places where the records of the research cite them: each entry has the key of the work, the sentence of the \
record, the place in the work, and the words of the work there ("quote"). These quotations are all that was read of \
the works. The session that compared the text found that none of them shows what the sentence attributes to the \
work, and "difference" says what the sentence attributes to the work and the quotations do not show.'''
COVERED_DECIDE = '''The paper asserts only what the research proved (method, section "What the running text asserts"), \
and it is written from the research as it stands: nothing is added to the library for the sake of a sentence. For each \
finding, therefore, cut the passage, or reword it so that it says no more than the element named with it. Reword where \
the reader needs what remains, as with a sentence that says what a lemma is for or that leads from one step to the \
next; cut where nothing would remain but the claim itself. Do not put an argument for the claim in its place: an \
argument written now has been checked by nobody, and this comparison exists to keep such text out of the paper. Where a \
later passage rests on what you cut, adjust it as far as the cut requires. A formula of a proof may stay in its proof \
as a step of the argument; what the finding asks for is that text outside the proof no longer uses it as a result that \
no element states, which a reference to the numbered statement that the element states can replace. When you find that \
an element does state what the passage asserts, keep the text and name that element in the note.

A finding about a cited work names no element, and it is answered from the quotations. Reword the sentence so that \
it says of the work what a quotation in `attributions.json` shows, at the place that the quotation has. The \
quotations of the work often show something near to what the sentence says: the result at another place, as a remark \
where the sentence has a theorem, for another quantity, or under another name. The sentence is then reworded to \
that. Where no quotation shows anything that the sentence could say of the work, take out what the sentence says of \
the work; the citation goes with it, unless the sentence says something else of that work which a quotation shows. \
The bibliography is the script's and stays as it is. The paper says no more about a work than was read (method, \
section "Results from the literature"), and what was read is what is quoted. What the sentence says about the \
objects of the paper is not the subject of such a finding and stays as it is. When you find that a quotation does \
show what the sentence says, keep the text and name the place of that quotation in the note.

One kind of passage has a third answer. A derivation that a proof of this section uses can stand outside that proof, \
as a computation that is carried out before the lemma whose proof relies on its result. Such a passage is a step of \
that proof. Outside the proof it reads as a result of the paper, which no element states; inside the proof it is part \
of the argument for the statement that the proof proves, and there the method does not hold it to the elements. So \
move the derivation into the proof, to the place where the proof uses it, and leave its words and its formulas \
exactly as they are. Change around it only what the move requires, such as the sentence that led up to the \
derivation or a reference to it. Answer such a finding with the action "moved". The script accepts a move when the \
passage that the finding quotes stands inside a proof of this section, unchanged, and no longer outside one, and \
when every formula of that passage which carries a label stands before each place that refers to it. It compares \
the words and the formulas of the quoted passage, with their labels, and disregards line breaks and spaces. A move \
does not answer the finding when text outside that proof relies on the result as well, be it the running text or \
another proof: the paper then uses the passage as a result. It is then cut or reworded as described above, or, \
where a cut would leave a proof without a step that it needs, kept with that reason.'''
# The answers that a repair of findings about the running text may give: "moved" is the third answer just described.
RESPONSE_MOVED = RESPONSE.replace('"revised" or "kept"', '"revised", "moved" or "kept"')

SECTION_KINDS = {
    'machine': '''The script's checks of the assembled manuscript found in this section the problems listed in \
`findings.json`. Each is a requirement of the method or of the plan. Correct every one.''',
    'wide': '''TeX typeset the manuscript, and some lines of this section came out wider than the text block, so that they \
stand out into the margin of the printed page. Some displayed formulas may also have less room on their line than they \
need: TeX then closes up the spaces inside the formula, or moves the number of the formula to a line of its own. \
`findings.json` lists these lines and formulas, with the lines of `paper.tex` they come from and by how much each is too \
wide. Where the line is a displayed formula, break the formula over two or more lines, with an environment such as \
`multline*` or `align*`; a formula with a number keeps its number and its label, in `multline` or in `equation` with \
`split` inside. Where it is a line of a paragraph, TeX found no place to break it: display the long formula, or reword \
the sentence. Change nothing in what the text says.''',
    'reading': READ_SECTION.format(compared='; another session compares that understanding with the research') + '''

''' + READ_DECIDE + READ_ELSEWHERE + ''' In every \
other case revise so that the next reader does not meet the same difficulty, which may mean rewriting the passage from \
the records in your brief instead of adjusting its wording.''',
    'comparison': COMPARED_SECTION + ' The whole manuscript is read again after this repair.',
    'likeness': LIKE_SECTION + '''

Rewrite this section so that at each of these places the manuscript does what the papers do: in the structure, the \
wording, the manner and the flow that the passages show, and as the papers in `exemplars/` write. ''' + LIKE_KEPT}

WHOLE_KINDS = {
    'machine': '''The script's checks of the assembled manuscript found the problems listed in `findings.json`. Each is a \
requirement of the method or of the plan. Correct every one.''',
    'typeset': '''TeX could not typeset the manuscript. `findings.json` holds the errors of the TeX run; line numbers in \
them are lines of `paper.tex`. Correct the cause of each error in the part where it lies, which need not be the part in \
which TeX noticed it.''',
    'reading': READ_WHOLE + '''

First compare the understanding with the research: with `root.md`, with the outline of the plan, and with the records \
of the main result and of the elements that its proof names. Where the reader understood something other than what \
these say, the manuscript did not convey it, whether or not a finding points there. Then decide for each finding whether \
the manuscript has to change. A reader can misread, and a finding can ask for something the method excludes; in that case \
keep the text and say why. In every other case revise so that the next reader does not meet the same difficulty, which \
may mean rewriting the passage from the records instead of adjusting its wording.''',
    'likeness': LIKE_WHOLE + '''

Rewrite the parts so that at each of these places the manuscript does what the papers do: in the structure, the wording, \
the manner and the flow that the passages show, and as the papers in `exemplars/` write. ''' + LIKE_KEPT}

# What a narrow repair is told in the place of the second half, the same for a section and for the whole. It is the
# last repair that its findings receive: no reading of the whole manuscript follows it, only a reading of the passages
# it changed, so it changes the passages that its findings name and nothing else.
NARROW_READ_BY = {None: 'The session that reported the findings has read every passage of the manuscript as it stands.',
                  'coverage': 'Every passage of the manuscript as it stands has been read by a session that read the '
                              'manuscript from beginning to end, or is a change that a session read where it stands.'}
NARROW_TEXT = '''After this repair no session reads the whole manuscript again. {read_by} After the repair another \
session reads the passages that the repair \
changed, and those only. For each of them it has the text before and the text after. It reads the new text where it \
stands in the manuscript and judges whether the change is sound: whether every step of an argument is still there, \
whether every statement still says what it said, and whether the notation and the references still agree with the rest \
of the manuscript. A change that it finds unsound is undone by the script, together with the other changes that were \
made for the same finding, and the finding is then reported as open. A change that it finds sound stays in the paper, and \
nobody reads that passage again. A finding for which you keep the text is reported as open as well, with your note.

So this repair is narrow. For each finding change the passage that the finding names, and change it only as far as the \
finding requires. What a finding requires can lie beside the passage it names, as when a term has to be defined before \
the sentence that uses it; such a change belongs to the answer and is made. Leave every other passage exactly as it is, \
also where you would write it otherwise or see a slip in it: a passage that is changed without a finding asking for it \
is one more passage that has to be judged, and when a change in it is found unsound, the repair of a finding can be \
undone with it. A finding that speaks of the manuscript throughout and names places as examples is answered at the \
places it names; say in the note that the other places stand as they were. Where a finding can be answered only by more \
than this, for example by rearranging a section or by writing a proof anew, keep the text and say in the note what would \
have to change.

In the note of a finding that you revise, say which passages you changed for it. The session that reads the changes \
has the notes, and tells from them which change belongs to which finding.'''
NARROW, NARROW_COVERED = (NARROW_TEXT.format(read_by=NARROW_READ_BY[kind]) for kind in (None, 'coverage'))
NARROW_AGAIN = '''

A finding that carries "open_because" was left open before this repair, and the text under that key says why. In one \
case an earlier repair took the finding up: it kept the text; or its change was found unsound and undone, so that the \
text is again as it was; or its change stayed in the text and was found not to answer the finding; or the finding was \
repaired and too few readings followed to confirm the repair. In the other case no repair has taken the finding up: a \
comparison reported it, and no repair followed that comparison. Decide about such a finding anew, on the text as it \
stands, with that reason in view.'''
NARROW_READ = ''' In every other case revise the passage that the finding names, so that a reader of the paper does not \
meet the same difficulty there.'''
NARROW_LIKE = '''At each of these places change the passage that the finding quotes, or add what the finding misses at the \
place it names, so that the manuscript does there what the papers do, in the manner that the passages under "evidence" \
show. '''
NARROW_TITLE = ''' The title of the paper stands in the plan, which a repair keeps: for a finding about the title, keep \
the text and say so.'''
NARROW_SECTION_KINDS = {
    'reading': READ_SECTION.format(compared='') + '\n\n' + READ_DECIDE + READ_ELSEWHERE + NARROW_READ + '\n\n' + NARROW,
    'comparison': COMPARED_SECTION + '\n\n' + NARROW,
    'likeness': LIKE_SECTION + '\n\n' + NARROW_LIKE + LIKE_KEPT + '\n\n' + NARROW,
    'coverage': COVERED_FINDINGS + '\n\n' + COVERED_DECIDE + '\n\n' + NARROW_COVERED}
NARROW_WHOLE_KINDS = {
    'reading': READ_WHOLE + '\n\n' + READ_DECIDE + NARROW_READ + NARROW_TITLE + '\n\n' + NARROW,
    'likeness': LIKE_WHOLE + '\n\n' + NARROW_LIKE + LIKE_KEPT + NARROW_TITLE + '\n\n' + NARROW}

SECTION_REPAIR_PROMPT = CONTEXT + '''

This session repairs one section of the manuscript that earlier sessions wrote: "{title}", whose id in the plan is \
`{id}`.{also} What was found in a section goes to a session for that section, and these sessions run side by side, so \
this session changes this section and no other.

In this folder:
''' + METHOD_BEFORE_CHECKS + '''
''' + BRIEF_FILE.format(tense='was') + ''' A repair keeps the plan: the same numbered statements, kinds, labels and \
order, the same notation.
''' + RESEARCH_FILES + '''
''' + PREFERENCES_FILE + '''
- `paper.tex` is the manuscript, which the script assembled from the parts as they stand. {spans} The rest of it is there \
to be read: what the reader has met before this section, and how the other sections use what this one states.
- `parts/` holds what this session may change, as it stands: {held}.
- `findings.json` holds what was found in this section.{papers}

{kind}

Write the complete new text of {what} as {outputs}, with the file name it has in `parts/`; leave a part out when it \
stays as it is.{response} As when the section was written, it refers to other sections only by `Section~\\ref{{sec:<id>}}` \
and by their numbered statements, and the labels it creates begin with `eq:{id}-` or `subsec:{id}-`. The script then \
assembles the manuscript again and repeats its checks. Use no source other than the files in this folder.
'''
SECTION_PAPERS_FILES = '\n' + STUDY_FILE + '''
- `exemplars/` holds {count} of those papers, {papers}, each as the LaTeX source that its authors wrote: the ones the \
plan names for this section.

Whatever you rewrite is written as those papers are written, in the sense of the method's section "The papers this \
paper is written like". Before you rewrite a paragraph, a proof or a section, read `study.md` and read the papers in \
`exemplars/` whole, from the title to the references. A repair that only corrects the LaTeX, or breaks a formula over \
two lines, needs the papers only to see how such a thing is set.'''

REPAIR_PROMPT = CONTEXT + '''

This session repairs the manuscript that earlier sessions wrote. It takes up what concerns no single section; what was \
found in one section goes to a session that repairs that section alone.

In this folder:
''' + METHOD_BEFORE_CHECKS + '''
- `plan.json` is the plan of the paper. A repair keeps it: the same numbered statements, kinds, labels and order, the \
same notation.
''' + RESEARCH_FILES + '''
''' + PREFERENCES_FILE + '''
- `parts/` holds the parts of the manuscript as they stand: `abstract.tex` and one file per section.
- `paper.tex` is the manuscript the script assembled from them. {spans}
- `findings.json` holds what was found.{papers}

{kind}

For every part you change, write its complete new text as `output/<name>.tex`, with the file name it has in `parts/`. \
Leave unchanged parts out.{response} The script then assembles the manuscript again and repeats its checks. Use no source \
other than the files in this folder.
'''
REPAIR_PAPERS = '\n' + STUDY_FILE + '''
- `exemplars/` holds the papers that the plan names for its sections, each as the LaTeX source that its authors wrote. \
For each section they are: {papers}.

Whatever you rewrite is written as those papers are written, in the sense of the method's section "The papers this \
paper is written like". Before you rewrite a paragraph, a proof or a section, read `study.md` and read whole the papers \
of the section in which you rewrite, from the title to the references. A repair that only corrects the LaTeX, or breaks \
a formula over two lines, needs the papers only to see how such a thing is set.'''

SECTION_FIELD = '''"section" says where the place lies, for the revision, which is made section by section: it is the \
label that stands in `paper.tex` directly after the heading of that section, such as "sec:proof", or "abstract" for the \
abstract. It is the empty string when the {finding} concerns the title, more than one section, or the paper as a whole.'''

READ_PROMPT = '''This folder holds the manuscript of a mathematical paper: `paper.tex`, its LaTeX source, and \
`references.bib`. Read the whole manuscript as the reader described below would read the paper, and report what you \
understood and where the reading failed. The report is used to revise the manuscript so that it serves that reader. A \
report that passes over a place where the reader would have stopped is of no use for that, and neither is a list of \
preferences about wording.

The reader:

{reader}

Use the two files and nothing else: no other file on this machine and no search.

Write `output/reading.json`, a JSON object with two keys.

- "understanding": {{"main_result": "...", "proof": "..."}}. In your own words: what exactly the paper proves, with its \
hypotheses and its conclusion; and how the proof goes, that is, which steps it has and which idea carries it.
- "findings": an array, empty when you have none. Each is {{"where": "...", "section": "...", "quote": "...", \
"problem": "..."}}: the section or the numbered statement, the exact words of the manuscript, and what is wrong or missing \
there together with what you would have needed. ''' + SECTION_FIELD.format(finding='finding') + ''' Report every place \
where you could not follow a step of an argument; where a term or a \
symbol is used before it is defined, or is never defined; where a reference points to something that is absent or comes \
later; where a proof does not prove what its statement says, or has a gap or an error; where the notation or the wording \
of one thing changes; and where the text does not belong in a mathematical paper, for example because it speaks of how \
the paper or its proofs were produced.
'''

LIKENESS_PROMPT = '''This folder holds the manuscript of a mathematical paper, `paper.tex`, its LaTeX source, with its \
bibliography `references.bib`, and in the folder `exemplars` four research articles from refereed journals, each as the \
LaTeX source that its authors wrote: {papers}. Read the papers and the manuscript as the text below describes, and report \
whether the manuscript is written as these papers are written. The report is used to revise the manuscript where it is \
written otherwise.

{section}

Use these files and nothing else: no other file on this machine and no search.

Write `output/likeness.json`, a JSON object with two keys.

- "likeness": a few sentences saying in what the manuscript is like the papers.
- "departures": an array, empty when you find no departure. Each is {{"where": "...", "section": "...", "quote": "...", \
"evidence": [...], "difference": "..."}}. "where" is the place in the manuscript: the part, the section or the numbered \
statement, or, when something is missing, the place where it would stand. ''' + SECTION_FIELD.format(finding='departure') + ''' \
"quote" is the passage of the manuscript, copied exactly from \
`paper.tex`, or the empty string when the departure is that something is missing. "evidence" is an array of \
{{"exemplar": "<the name of the paper's file without .tex>", "quote": "..."}}: the passages, copied exactly from the \
papers, that show the practice from which the manuscript departs, as the text above asks for them. "difference" says \
what differs and what a paper written like these would have at that place.
'''

COMPARE_PROMPT = CONTEXT + '''

This session compares the numbered statements of one section of the manuscript, "{title}", with the statements they come \
from; other sessions do the same for the other sections. The paper is of use only if each of its numbered statements \
says exactly what was proved.

In this folder:
- `paper-method.md` is the method the manuscript was written by, here without its last two sections, which other \
sections name and which say what each session is given and how a manuscript is checked. Its sections "What of the canon \
the paper leaves out" and "Every numbered statement says what its element says" say what a numbered statement has to \
say and which differences from the record are permitted.
- `statements.json` lists {listed}: for each its label, its number, the element it \
states, the statement of that element in words as its record gives it, the element's Lean statement, and the statement \
as the manuscript has it.
- `records.md` holds the records in full of the elements that these statements state, and, by what they say, the \
elements that their statements mention, each with the symbol or name under which the paper knows it where the plan fixes \
one.
- `elements/` holds the full record of every element that the proof of the root rests on, one file each, and \
`elements.md` lists the elements with their files. Open one when a statement speaks of an object whose definition you \
need and `records.md` does not give it.
- `paper.tex` is the manuscript, for the definitions and the notation in which its statements are read. {spans}

For each entry decide whether the statement of the manuscript says exactly what the statement of the element says: the \
same objects, the same hypotheses, the same quantifiers and ranges, the same conclusion, neither stronger nor weaker, \
read with the definitions and the notation of the manuscript. A difference the method permits is no difference as long \
as the mathematical content is the same. Where a convention changed, for example an index that now starts at one, check \
that the statement was carried over correctly, case by case at the boundary. Where the statement in words and the Lean \
statement of an element disagree with each other, the Lean statement is the one that was proved: give the verdict by \
it, and report the disagreement in "record_disagreement": it lies in the element's record, which no repair of the \
manuscript can change.

A statement that the paper takes from the literature carries its citation in the brackets that follow the opening of \
its environment: the work, and the place in it where the result stands. The record of its element names the work in \
its header and the place in its part "Literature". Hold the citation to the record as well. When the manuscript names \
another work, or another place in the work, such as another theorem number or a remark where the record has a \
theorem, the verdict is "differs", and "difference" says what the record gives.

Write `output/comparison.json`: an array with one object for each entry, {{"label": "...", "verdict": "same" or \
"differs", "difference": "<what differs, exactly; empty when the verdict is same>", "record_disagreement": "<where the \
statement in words and the Lean statement of the element disagree, exactly; empty when they agree>"}}. Use no source \
other than the files in this folder.
'''

CHANGES_PROMPT = '''This folder holds the manuscript of a mathematical paper, `paper.tex`, its LaTeX source, with its \
bibliography `references.bib`, and a file `changes.json`. The manuscript was read from beginning to end, and what that \
reading found went to repair sessions, which then changed some passages. Nobody has read the manuscript since. \
`changes.json` lists every passage that differs from the text that was read, each with its text before and after. This \
session reads each changed passage where it now stands and says whether the change may stay.

Your report decides that. The script undoes a change that you report as unsound, so that the passage reads again as it \
did when it was read. A change that you report as sound becomes part of the paper, and no one reads that passage again \
before the paper is handed over. So a change that is passed without having been read in its place lets an unread passage \
into the paper, and a sound change that is faulted for its wording throws away a repair.

The reader for whom the paper is written:

{reader}

`changes.json` is a JSON object with two keys.

- "findings": the findings that the repair sessions answered by changing the manuscript, each {{"finding": <its number>, \
"check": <what reported it>, "reported": <the finding as it was reported>, "repair": <what the repair session says it \
changed>}}. A finding of a reading of the manuscript by itself gives a place where a reader could not follow, missed \
something or found an error ("where", "quote", "problem"). A finding of a reading beside real papers gives a place where \
the manuscript is written otherwise than research articles are, with passages from such articles that show what they do \
there ("where", "quote", "evidence", "difference"). A finding of the comparison comes from a session that compared each numbered statement of the \
manuscript with the result of the research which it states. It gives a statement, by its label, that was found to say \
something else, and the difference ("label", "difference"); you do not have the research, and the difference as it is \
reported is what such a finding asks to be corrected. A finding of the comparison of the running text comes from a \
session that compared the text outside the numbered statements and the proofs with the results of the research. It gives \
a passage that asserts something which none of those results states, and what the passage asserts beyond the result \
that comes nearest ("where", "quote", "asserts", "difference"; "nearest" is the research's own name for that result and \
names nothing in the manuscript). Where it has "source" in the place of "nearest", the passage says something of the \
cited work with that key, and "difference" is what it says of the work beyond what was read of the work. Such a \
finding asks that the passage be cut, or reworded so that it no longer asserts that difference. A derivation that a \
proof uses has a third answer: it is moved into that proof as it is, where it is a step of the argument and no longer \
a result of the paper, so one change takes the passage out and another has it in the proof. The finding is answered \
when the manuscript no longer asserts the difference at that place, and a cut is sound when nothing that stays in the \
manuscript rests on what was cut. The array is empty when the only changes are corrections of the LaTeX.
- "changes": the changed passages in the order of the manuscript, each {{"change": <its number>, "part": <"abstract", or \
the id of the section, which follows `sec:` in the label after its heading>, "lines": <the lines of `paper.tex` at which \
the new text stands, or the line after which text was taken out>, "before": <the passage as it was read>, "after": <the \
passage as it stands now, empty when text was taken out>, "findings": <the numbers of the findings whose repair session \
changed this part, so that the change can have been made for any of them>}}. A passage is a run of whole lines of the source, so "before" and "after" may begin or end inside a \
sentence; the sentence is whole in `paper.tex`. A change whose "findings" is empty was made by a session that corrected \
the LaTeX after the script's checks or the typesetting, for example by breaking a formula over two lines.

Read the manuscript far enough to know its notation and how its proof goes. Then, for each change, read `paper.tex` \
around the lines given, as far as the passage reaches into its surroundings: the whole proof when the change lies in a \
proof, the statement and the places that use it when the change lies in a statement or a definition, the paragraphs \
around it otherwise. Compare the new text with "before". The change is sound when all of this holds of the new text in \
its place:

- No step of an argument is lost. What the old text proved, derived or justified is still proved, derived or justified, \
and for the same cases: a bound that was shown for every value of a parameter is not now shown at one value, and a case \
that the old argument covered is still covered by the new one, whether or not it has a sentence of its own.
- Every statement says what it said: the hypotheses, the quantifiers, the ranges and the conclusion of a numbered \
statement, a definition, a formula. The one exception is a correction that a finding asked for, which changes what the \
finding says is wrong and nothing else.
- The notation and the references agree with the rest of the manuscript. A symbol or a term of the new text is defined \
before it is used and means what it means elsewhere. A symbol or a term that the old text introduced, and that later \
text uses, is still introduced. Every `\\ref`, `\\eqref` and `\\cite` of the new text points to something that the \
manuscript has, and a label that the old text defined, and that other text refers to, is still defined.
- The new text is correct mathematics and correct LaTeX, as far as reading it shows.

How you would have worded the passage is not in question. A change that makes the text longer or shorter, plainer or \
stiffer, is sound when these hold. The passages that were not changed are not in question either, since they were read \
before. They count as the surroundings of a change: a change that is wrong because of what stands around it is not \
sound.

Say also for which findings each change was made: those among the numbers at the change to whose "reported" or \
"repair" the change corresponds. The changes made for one finding are one answer to it, and when one of them is \
unsound the script undoes all of them together. So name a finding at every change that belongs to its answer, and name \
none at a change that corresponds to no finding. Judge each change by itself all the same: a change that is sound is \
reported as sound, also when another change made for the same finding is not.

Then say for each finding whether the changes made for it answer it, that is, whether at the place the finding names \
the manuscript no longer has what the finding reported. Judge this from the finding as it was reported and from the \
manuscript as it stands, with every change in it. A change can be sound and leave its finding unanswered; it then stays \
in the paper, and the finding is reported as open with your reason.

Use the three files and nothing else: no other file on this machine, and nothing from the web.

Write `output/verdicts.json`, a JSON object with two keys.

- "changes": an array with one object for each change of `changes.json`, in their order: {{"change": <its number>, \
"sound": true or false, "findings": [<the numbers of the findings it was made for>], "reason": "..."}}. For a change that \
is not sound, "reason" says exactly what is lost, altered or inconsistent, with the words of the manuscript. For a sound \
change it says in a sentence what you read to judge it.
- "findings": an array with one object for each finding of `changes.json`, in their order: {{"finding": <its number>, \
"answered": true or false, "reason": "..."}}. For a finding that is not answered, "reason" says what the manuscript \
still has at that place; otherwise it may be empty.
'''

SKETCH_PROMPT = CONTEXT + '''

This run of the script makes the draft of the paper, and not yet the paper. The library can still be changed now, and \
the method's section "The draft that comes before the paper" says what the draft is for and what becomes of it.

This session sketches one section of the paper: "{title}", whose id in the plan is `{id}`.{also} Other sessions sketch \
the other sections at the same time. A sketch contains no prose of the paper. It fixes what the section will state: its \
numbered statements, the displayed formulas that are used as results, and whatever else the section will assert that no \
element states. Sessions after this one compare each sketched statement with its element. When the library is frozen, a \
writing session receives the same files as you, with the statements and formulas of your sketch, and writes the section.

In this folder:
''' + METHOD_BEFORE_CHECKS + '''
''' + BRIEF_FILE.format(tense='will be') + '''
''' + RESEARCH_FILES + '''
''' + STUDY_FILE + '''
- `exemplars/` holds {count} of those papers, {papers}, each as the LaTeX source that its authors wrote. The plan names \
them for this section as the ones from which the most can be learned for a section of this kind.

What the plan gives this section: {content}

Work as the writer of the section would, up to the point of writing. Read the brief, `study.md` and the papers in \
`exemplars/`, and decide how the section will go: in which form each statement is given, how each proof proceeds from \
the proof in its record, what the text between the statements says, and what a section of this kind in those papers \
would tell its reader. A gap that is not seen now is met by the writer, who can then only leave the sentence out. So \
take the section far enough to know every statement, every formula and every claim that it will rely on.

Write `output/sketch.json`, a JSON object with the three keys below. A text that will be printed is LaTeX in the \
notation of the plan; inside a JSON string a backslash is written twice.

- "statements": one object for each numbered statement that the plan has this section state, in the order of the plan: \
{{"label": "...", "text": "...", "gap": null}}. "label" is the label the plan gives the statement. "text" is the statement \
as the paper will have it, complete, as it stands between the `\\begin` and the `\\end` of its environment: with every \
hypothesis, in the notation and the conventions of the paper, written from the record as the method's section "Every \
numbered statement says what its element says" describes. "gap" is null when the text says exactly what its element \
says. Sometimes a paper would state the result otherwise than the element does: a classical bound in the strict form in \
which the literature has it where the element proves a weaker one, a lemma in its general form where the element has \
one value of a parameter, a statement at the parameters that the later proofs of the paper use, or only those parts of \
a result that the paper uses where the element states several parts together. Then write the text as \
the paper should state it, and give under "gap" an object {{"wanted": "...", "has": "...", "reason": "..."}}: "wanted" is \
the mathematical statement that the library would have to contain for the text to be covered, complete enough that a \
session which has the library and not this sketch can formalise it; "has" is what the element states instead; \
"reason" says why a paper would state it in the wanted form.
- "formulas": the displayed formulas that the section will use as results, each {{"label": "...", "host": ..., "text": \
"...", "element": ..., "gap": null}}. A formula belongs here when text outside the argument in which it stands will \
refer to it: a formula that is displayed in one proof and to which a later proof or the running text refers, or one \
that is displayed in the running text and that a proof uses. A formula that is a line of one computation and is \
referred to only inside that proof is not listed. "label" is the label the formula will carry: `eq:{id}-` followed by \
lowercase letters, digits and hyphens. "host" is the label of the numbered statement in whose proof the formula stands, \
or null when it stands in \
the running text. "text" is the formula as it will be displayed, without its environment. "element" is the name of the \
element that states exactly this formula, which may be a step that the plan absorbs at that place, or null when no \
element states it. In the first case "gap" is null. In the second, "gap" is {{"element": "...", "wanted": "...", "has": \
"...", "reason": "..."}}, with "element" the name of the element whose statement comes nearest and the other three as \
for a statement.
- "assertions": whatever else the section will assert about the objects of the paper that no element states, each \
{{"host": ..., "element": "...", "wanted": "...", "has": "...", "reason": "..."}}, with "host" as for a formula and \
"element" the element that comes nearest. The method's section "What the running text asserts" says what the paper may \
assert outside its numbered statements: a consequence drawn after a proof, a remark that a bound is sharp and the value \
of a result in a special case each have to be stated by an element. What an element states, or a special case or a weaker \
form of it, is no gap. Neither is a step of a proof that the record of the element gives, a fact that the reader \
knows from the textbooks of the area, or a sentence that says what the section does. An empty array when there is \
nothing of this kind.

Look in particular for a step that two proofs share. When a proof of this section derives a fact that another proof \
of the paper also uses, in this section or in another, the paper can state that fact once only if an element states \
it. Without such an element the second proof repeats the derivation, or it refers to a formula inside the first \
proof, and the paper then uses as a result something that no element states. This holds also for a step that the \
record of an element gives inside its proof and that is no element itself: inside the one proof it is no gap, and \
once a second proof uses it, it is used as a result. A fact of the textbooks stays what it is, however many proofs \
use it. Whether another proof uses a fact, you judge from the records of the elements. So where no element states \
the shared fact, and the proof that derives it first, in the order of the paper, belongs to this section, list it: \
under "formulas", with its gap, when it will be a displayed formula, and under "assertions" otherwise, with the \
fact that both proofs use as "wanted", the label of the statement in whose proof it is derived as "host", and under \
"reason" the two proofs that use it. Where that first proof belongs to another section, the session of that section \
lists the fact. The library can then receive it as a declaration, which both proofs use as they use a lemma.

A gap that is declared is no fault of the sketch, and what harms the paper is one that is not declared; the method's \
section "The draft that comes before the paper" says what becomes of each. Declare a gap only where a paper would in \
fact state the result in that form; a statement is not strengthened because a stronger one looks attainable.

Write no part of the paper itself. Use no source other than the files in this folder.
'''

DRAFT_COMPARE_PROMPT = CONTEXT + '''

This run of the script makes the draft of the paper, and not yet the paper: for each section a session has sketched \
the numbered statements as the paper will state them and the displayed formulas that the section will use as results. \
The library can still be changed, and what the draft wants beyond it goes to sessions that try to add it. This session \
compares the sketched statements and formulas of one section, "{title}", with the elements they are to state; other \
sessions do the same for the other sections. The paper is of use only if each of its statements says exactly what was \
proved, and a difference that is not found here is written into the paper.

In this folder:
- `paper-method.md` is the method the paper is written by, here without its last two sections, which other sections \
name and which say what each session is given and what is done once a manuscript is written. Its sections "What of \
the canon the paper leaves out" and \
"Every numbered statement says what its element says" say what a statement has to say and which differences from the \
record are permitted. Its section "The draft that comes before the paper" says what a gap is.
- `statements.json` lists the sketched statements and formulas of this section: for each its label, whether it is a \
numbered statement or a formula, the element it is to state, the statement of that element in words as its record gives \
it, the element's Lean statement, the sketched text ("draft_statement"), and "declared_gap". "declared_gap" is null, or \
it holds what the sketching session said of the entry: that its text on purpose says something other than the element, \
with what the paper wants, what the element has, and why.
- `records.md` holds the records in full of the elements that these entries state, and, by what they say, the elements \
that their statements mention, each with the symbol or name under which the paper knows it where the plan fixes one.
- `elements/` holds the full record of every element that the proof of the root rests on, one file each, and \
`elements.md` lists the elements with their files. Open one when an entry speaks of an object whose definition you need \
and `records.md` does not give it.
- `plan.json` is the plan of the paper. Its "notation" is the notation in which the sketched texts are written; no \
manuscript exists yet.

For each entry decide whether the sketched text says exactly what the statement of the element says: the same objects, \
the same hypotheses, the same quantifiers and ranges, the same conclusion, neither stronger nor weaker, read with the \
notation of the plan. A difference the method permits is no difference as long as the mathematical content is the same. \
Where a convention changed, for example an index that now starts at one, check that the statement was carried over \
correctly, case by case at the boundary. Where the statement in words and the Lean statement of an element disagree \
with each other, the Lean statement is the one that was proved: give the verdict by it, and report the disagreement in \
"record_disagreement".

An entry whose "declared_gap" is not null is expected to differ, and is judged like the others. When it differs, the \
gap goes on to the sessions that extend the library, and nothing more is asked of you for it. When you find that it says \
what its element says after all, give the verdict "same": the gap is then dropped. An entry without a declared gap \
that differs is a slip of the sketch. For such an entry give under "text" the statement as the element says it: \
complete, in the notation of the plan, written as the method describes, so that it can stand in the paper in the place \
of the sketched text. The script puts it there, and nobody compares it again before the paper is written.

One difference of an entry without a declared gap is treated otherwise. An element can state several things together, \
for example a lemma in four parts, or two bounds joined by "and". A sketched text that gives some of these parts and \
leaves the others out says less than its element, so it differs. If the script put the full statement in its place, \
the paper would state parts that it never uses, readers would ask what those parts are for, and the parts could not \
be dropped, because a numbered statement says what its element says. While the library can still be changed, there \
is a better answer, which is a declaration that states the used parts alone. So when the sketched text states some \
of the parts of its element, \
each as the element states it, up to the differences that the method permits, and asserts nothing else, give the \
verdict "differs", say under "difference" which parts the text states and which it leaves out, and set "partial" to \
true. The script then keeps the sketched text and asks the sessions that extend the library for a declaration that \
states those parts alone, so "text" stays empty for such an entry. A text that leaves out a part and also changes \
one of the parts it keeps is a slip like any other, and "partial" is false. So is a text that states the whole \
element more weakly, for one value of a parameter or on a smaller range: it leaves out no part.

Write `output/comparison.json`: an array with one object for each entry, in their order, {{"label": "...", "verdict": \
"same" or "differs", "difference": "<what differs, exactly; empty when the verdict is same>", "text": "<for an entry \
without a declared gap that differs, unless it is partial: the statement as the element says it; otherwise empty>", \
"partial": <true when an entry without a declared gap differs only by leaving out parts of its element, as \
described above; otherwise false>, "record_disagreement": \
"<where the statement in words and the Lean statement of the element disagree, exactly; empty when they agree>"}}. Use \
no source other than the files in this folder.
'''
# Why a drafted text that states only some of the parts of its element is a gap, in the words of the gap (Paper.draft).
PARTIAL = ('The paper uses only these parts of what the element states. A statement of the paper says exactly what one '
           'declaration states, so the paper can state these parts alone only when a declaration states them alone; '
           'such a declaration follows from the element at once.')

PLAN_REPAIR_PROMPT = CONTEXT + '''

This paper was drafted before the library had its final form. A session planned it, and for each section the numbered \
statements were sketched and compared with the library. The library was then changed and frozen: declarations were \
added so that it contains what the draft wanted, some were renamed or removed, and sources were entered into records. A \
script has carried the plan of the draft over to the library as it is now: an element that is gone left the plan, a \
declaration that closed a gap entered where the gap stood, and a statement whose element now has a source is cited. \
The plan that came of this does not pass the check that every plan passes before sections are written from it. This \
session repairs that plan. It does not plan the paper anew: the papers were chosen and read, the statements were \
drafted under the labels of this plan, and the writers will receive those drafts.

In this folder:
''' + METHOD_BEFORE_CHECKS + '''
- `plan.json` is the plan as the script carried it over, and `carried.md` says what the script changed in it.
- `problems.md` lists what the check of the plan found. These are the reasons the script cannot write the paper from \
`plan.json`.
- `draft.json` holds the drafted statements, under "statements", and the drafted formulas, under "formulas", by their \
labels, each with the element that states it now. An entry with "cut" is not used.
- `materials-digest.md` is a digest of the materials as the frozen library has them: everything the proof of the root \
rests on, and the declarations that closed a gap of the draft with what they rest on, which the digest marks as added \
for the draft where the proof of the root does not use them. `elements/` holds the full record of every element, one \
file each; the digest names the file at each element.
- `study.md` is the account that the planning session wrote of how the papers it chose are written. The papers \
themselves are not in this folder and are not read again. The plan keeps its "exemplars" as they are, and so does every \
section; a section that you add names two of the plan's papers.

Change in the plan what the problems require, and leave the rest as it is. The labels, the kinds, the sections and the \
elements of the numbered statements in particular stay wherever no problem requires otherwise, because the drafted \
texts belong to them by their labels. Where a problem leaves a choice, make it as the method does. An element that the \
library gained and that the plan does not mention is placed by its weight and by what uses it, as the method's \
section "Which elements receive a number" describes. An element that lost its place, because the statement it was \
absorbed into no longer rests on it or because the section that held it is gone, is placed anew in the same way. An \
element that another now stands for is recorded as not stated, with that element under "by".

Write `output/plan.json`: the complete plan, a JSON object with the keys below, as the session that planned the paper \
was told them. A plan may also have the key "citations", an array, which names results that an earlier step asked to \
have cited; leave out of it every element whose record now names a source, and every element that is gone.

{plan_keys}

Use no source other than the files in this folder. Write no part of the paper itself.
'''

RESOLVE_PROMPT = CONTEXT + '''

This session resolves what the readings of the manuscript left open. The manuscript was written, read and repaired by \
sessions before this one. It was read by sessions that had nothing but the manuscript, as its reader will read it, and \
it was read beside research articles from refereed journals, as the method's section "Reading the manuscript beside \
real papers" describes. What these readers found went to repair sessions a \
bounded number of times. Each of those repairs kept the plan of the paper, and the last ones were narrow: they changed \
the passages that their findings named and nothing else. `findings.json` holds the findings that are open after all of \
that. Many of them are open because no repair of that kind could answer them. A reader beside real papers finds that a \
section gives a full proof where papers give a sentence, or that two sections do what papers do in one; a reader of the \
manuscript finds a statement that stands before the notion it needs. Such findings ask for another arrangement of a \
section, for a statement in another place or without a number of its own, for a passage written anew.

This session can answer such a finding, because it is not bound to the plan. It is also the last that takes these \
findings up: each of them is closed here, by a change of the manuscript or by your reason for leaving the text as it \
is. The reasons are handed over with the paper, to the person who decides whether the paper is as it should be.

In this folder:
''' + METHOD_BEFORE_CHECKS + '''
- `plan.json` is the plan of the paper as the manuscript now follows it.
''' + RESEARCH_FILES + '''
''' + PREFERENCES_FILE + '''
- `parts/` holds the parts of the manuscript as they stand: `abstract.tex` and one file per section.
- `paper.tex` is the manuscript the script assembled from them. {spans}
- `findings.json` holds, under "findings", the open findings, each {{"finding": <its number>, "check": <the reading that \
reported it>, "reported": <the finding as it was reported>}}. A finding of a reading of the manuscript by itself gives a \
place where a reader could not follow, missed something or found an error ("where", "quote", "problem"). A finding of a \
reading beside real papers gives a place where the manuscript is written otherwise than research articles are, with \
passages from such articles that show what they do there ("where", "quote", "evidence", "difference"). Where a finding \
carries "open_because", the text under that key says why it is still open: a repair kept the text and gave its reason; \
or its change was found unsound and was undone; or its change stayed and was found not to answer the finding; or the \
finding was repaired and too few readings followed to confirm the repair. Under "understanding" the file holds what the \
last reader of the manuscript took the paper to prove and how, or null.{papers}

What you may change. You may rewrite a passage, a proof or a whole part. You may also change the structure of the \
paper: move a numbered statement to another place or another section; change its kind; take away its number and write \
its content into the running text or into the proof that uses it; give a number to an element that the plan absorbed; \
join two sections or divide one; change the title of the paper or of a section; change an entry of the notation. Which of these a finding calls for is \
yours to judge, by the method and by what the papers in `exemplars/` do.

What stays, and why. Every numbered statement states one element of the materials and says exactly what that element \
says, because that correspondence is what the paper is worth; you may reword a statement, and you may not change what \
it says or add a numbered statement that states no element. The paper asserts no mathematics that the elements do not \
state (method, section "What the running text asserts"): nothing can be added to the library now, and after this \
session the running text is compared with the records, where a sentence that no element covers is cut. The paper cites only works that are \
in `references.bib`, and it does not mention Lean, a proof assistant or a formal proof. The other decisions of the \
method stand as well, also where the papers do otherwise.

Decide for each finding whether the manuscript has to change. A reader can misread, and a finding can ask for \
something that the method excludes or that would change the mathematics; in that case keep the text and say why, in \
words that the person who receives the paper can judge without this folder. In every other case change the manuscript \
so that a reader no longer meets what the finding reports, at the place the finding names and wherever else the same \
thing stands. No sentence of the papers is copied or paraphrased into the manuscript; they show manner.

What you write:

- For every part you change, its complete new text as `output/<name>.tex`, with the file name it has in `parts/`. The \
part of a section that you create is `output/<id>.tex`, with the id you give that section in the plan. Leave unchanged \
parts out.
- `output/plan.json`, when you change the structure: when a numbered statement moves to another section, changes its \
kind or its label, loses or gains its number or is now cited; when sections are joined, divided or reordered; when a \
title or the notation changes. It is the complete plan in the form of `plan.json`, changed so that it says what the \
manuscript now is, because the script holds the manuscript to the plan: every numbered statement of the plan in its \
section, in the plan's order, with its kind and label, and no other. A statement that loses its number moves from \
"statements" to "others", with the treatment "absorbed" and the place into which it is now written. A section that is \
gone is left out, and its part with it. The plan keeps its "exemplars"; a section that you create names two of them. \
When the structure stays as it is, write no plan.
- `output/response.json`: an array with one object for each finding of `findings.json`, in their order, {{"finding": \
<its number>, "action": "revised" or "kept", "note": "..."}}. For a finding that you revise, the note says what you \
changed and where. For a finding that you keep, the note is your reason, complete in itself, since it is what the \
person who receives the paper reads about that finding.

The keys of a plan, as the session that planned the paper was told them:

{plan_keys} A plan that the script cannot accept comes back to a new session with the reasons.

After this session the script assembles the manuscript and repeats its machine checks and the typesetting. A session \
that has nothing but the manuscript then reads it from beginning to end, the numbered statements whose text changed are \
compared with their elements, and the running text is compared with the records. Nobody else reads what you rewrite \
with the research beside it. So a proof that you rewrite is rewritten from the proof in the record of its element, step \
by step, and not from the proof in the manuscript alone. Use no source other than the files in this folder.
'''

COVER_PROMPT = CONTEXT + '''

This session compares the running text of one section of the manuscript, "{title}", with what the research proved; \
other sessions do the same for the other sections. The numbered statements of the manuscript have each been compared \
with the element they state. The text around them has not: the sentences that introduce a lemma, that draw a \
consequence after a proof, that say what a bound gives in a special case or that a result cannot be improved. Such a \
sentence can assert more than was proved, and nothing in the paper would show it. The paper is written from the \
research as it stands, and nothing is added to the library for the sake of a sentence. What this session reports is \
therefore cut from the paper, or reworded, by a repair session.

In this folder:
- `paper-method.md` is the method the manuscript was written by, here without its last two sections, which other \
sections name and which say what each session is given and how a manuscript is checked. Its section "What the running \
text asserts" says what the paper may assert outside its numbered statements and when an element covers an assertion. \
That section leans on two others: "The reader", which says what the reader of the paper knows from the textbooks, and \
"Results from the literature".
- `text.json` lists what this session compares, each entry with its number ("entry"), its kind, the part it stands in \
("part", the id of this section{abstract}), the lines of `paper.tex` it occupies and its text. An entry of the kind \
"running text" is a passage of the section outside the numbered statements and outside the proofs. An entry of the \
other kind is a displayed formula inside a proof to which text outside that proof refers, by one of the labels under \
"labels": the manuscript uses such a formula as a result, so it is held to the elements as the running text is.
- `records.md` holds the records in full of the elements whose records the writer of this section had in full, and \
every other element that the proof of the root rests on by what it says, each with the place where the paper has it \
and the symbol or name under which the paper knows it.
- `elements/` holds the full record of every element, one file each, and `elements.md` lists the elements with their \
files. Open one when the statement in `records.md` does not settle whether an element covers an assertion.
{attributions}- `paper.tex` is the manuscript, for the definitions and the notation in which its text is read, and for the place of \
each entry. {spans}

Read each entry where it stands in `paper.tex`. Find in it every assertion of mathematics about the objects of the \
paper: every sentence or formula that says that something holds, follows, equals, is bounded, exists, fails or cannot \
be improved. For each assertion look for an element that covers it, as that section of the method describes. Read \
both in the notation and the conventions of the manuscript. Where the statement in words and the Lean statement of an \
element differ, the Lean statement is what was proved. Check a special case at its boundary: an element that is stated \
for $n \\ge 1$ does not cover a sentence about $n = 0$.

Report every assertion that no element covers. Report it also when it is true and its proof would be short: the \
question is whether the library states it, and a claim that is easy to prove is as unproved there as a hard one. An \
assertion that follows only from two elements together, and that no single element states, is not covered.

That section of the method also says what in the running text is no assertion in this sense, and none of that is \
reported. And how a passage is worded is not in question.{main}

{literature}

Write `output/coverage.json`: an array, empty when an element covers every assertion{sourced}. Each object is {{"entry": <the \
number of the entry>, "quote": "<the sentence or the formula, copied exactly from the entry>", "asserts": "<what it \
asserts, in a sentence>", "nearest": "<the name of the element whose statement comes nearest to it>", "difference": \
"<what the passage asserts that this element does not state, exactly>"}}.{source} Use no source other than the files in this \
folder.
'''
# What a session that compares the running text is told about sentences on the literature: without the quotations
# from the cited works they are not its subject, and with them (a paper written from a draft that carries
# "attributions") each such sentence is held to what was quoted.
COVER_LITERATURE = ('What the text says about the literature is not the subject of this comparison: the method\'s '
                    'section "Results from the literature" governs it.')
COVER_ATTRIBUTIONS = '''What the text says about the literature is compared as well, against another source. Before \
this paper was written, a session opened the works that the records of the research cite and copied, for every \
sentence of a record that attributes something to a work, the words of the work at the place which that sentence \
names. `attributions.json` holds these: for each the key of the work in the bibliography ("key"), the element whose \
record has the sentence ("declaration"), the sentence of the record ("sentence"), the place in the work ("place"), \
and the words of the work there ("quote"). They are all that anybody read of these works for this paper, and the \
paper says no more about a work than was read (method, section "Results from the literature"). Records that nobody \
had held against the works have attributed wrongly in these ways: a theorem cited for a quantity that it does not \
treat, a remark cited as a theorem, a family of objects called by a name that the cited authors do not use, a number \
said to be printed at a place where it is not, and a work that could not be opened at all.

So go through the entries once more for every sentence of the manuscript that says something of a cited work: what \
it states, proves, defines or tabulates, what its authors call an object, where in it a result stands. Such a \
sentence is supported when a quotation from that work in `attributions.json` shows what the sentence attributes to \
the work. Where the sentence of the manuscript names a place in the work, such as the number of a theorem or a page, \
the quotation that supports it is one from that place; where it names none, a quotation from any place of the work \
supports it. Report each sentence that no quotation supports, also when what it attributes is plausible, and report \
a sentence about a work of which `attributions.json` has no quotation. A sentence that only names a work, without \
saying what is in it, attributes nothing and is not reported. A sentence that says what a work does not contain, or \
does not do, cannot be shown by words of the work; it is supported when a sentence of a record in \
`attributions.json` says the same of that work. A sentence can do two things at once: assert \
mathematics about the objects of the paper, and attribute it to a work. It is then held to both. An element has to \
cover what it asserts, a quotation has to support what it attributes, and it is reported once for each of the two \
that fails.'''
COVER_SOURCE = (' For a sentence about a cited work, as described above, the object has "source": "<the key of the '
                'work in the bibliography>" in the place of "nearest"; its other keys are those of every object, and '
                '"difference" says what the sentence attributes to the work that the quotations do not show.')

# What the session that covers the first section is told about the abstract, which states the main result.
COVER_ABSTRACT = '''

The abstract is among the entries, and it states the main result of the paper. A reader meets the abstract without \
the paper, so nothing in the paper can supply a restriction that the abstract leaves out. Hold what the abstract says \
of the main result to the element of the main result, `{name}`, as a numbered statement is held to its element. The \
abstract may say the result in words, and it need not repeat everything that the theorem says. But what it says has \
to hold in every case that it speaks of. Where it drops a restriction of a range or a hypothesis, so that its \
sentence claims cases which the element does not state, it asserts more than was proved: an abstract that says "for \
every $n$" where the theorem has $n \\ge 1$ is such a case. Report it like every other assertion that no element \
covers, with that element under "nearest". Every other assertion of the abstract is treated as the running text of \
the section is.'''

PLACE_PROMPT = CONTEXT + '''

This session checks one list of a file that the script writes beside the paper, `correspondence.json`. The paper \
has numbered statements: its theorems, propositions, lemmas, corollaries and numbered definitions. Not every element \
of the research has one. The plan of the paper, which an earlier session made and from which the sections were \
written, wrote some elements into the statement or the proof of a numbered statement, or into the running text of a \
section, that is, the text outside the numbered statements and the proofs; and it had some results from the \
literature cited in the running text of a section. The list says for each of these elements where the paper has its \
content, so that somebody who starts from a declaration of the library finds the place in the paper. It was made \
from the plan. Since the sections were written they have been repaired, and a repair can reword a sentence, move it \
into a proof or cut it, so the plan no longer shows where the content stands. This session reads the manuscript as \
it stands and says, for each element of the list, whether the manuscript has its content and where.

In this folder:
- `paper.tex` is the manuscript, in LaTeX. {spans}
- `placed.json` holds the entries of that list. Each entry has the name of the element ("element"), its statement in \
words, or in Lean where its record has none in words ("statement"), what the plan did with it ("treatment": "absorbed" \
or "cited"), and the places that the plan gave it ("planned"). For an absorbed element these are the label of each \
numbered statement into whose statement or proof it was written, and the label of each section, such as \
`sec:tools`, into whose running text it was written. For a cited element it is the label of the section whose \
running text cites the result.
- `elements/` holds the full record of every element, one file each, and `elements.md` lists the elements with their \
files. Open the record of an element when its statement does not tell you what to look for in the text, as with a \
definition that the paper gives only as a notation, or a step that is one line of a computation.

The manuscript names no element, so an element is found by its content. An absorbed element has no numbered \
statement of its own in the paper. Its content is a definition given in a sentence, a step carried out inside a \
proof, or a fact used in a clause. The manuscript has it when, at some place, it says or carries out what the \
element states, in the notation of the paper; the words of the record need not be there. A cited element is in the \
manuscript when the text cites the result from its source and says what the result is. The manuscript does not have \
an element when no place has anything of its content, as when the sentence that gave a definition was cut or a proof \
now reaches its conclusion without the step. Where the content is there only in part, in a weaker or a stronger \
form, or otherwise than the plan had it, as with a result that is now proved where the plan had it cited, the \
element counts as found, and the note says what differs.

Write `output/placement.json`: an array with one object for each entry of `placed.json`, in their order: \
{{"element": "<its name>", "found": true or false, "where": "<each place that has its content now, in the order of \
the manuscript, with a semicolon between two places; a place is the label of the section, or the word abstract, \
followed by a comma and the label of the numbered statement when the place is that statement or its proof, as in \
sec:tools, lem:step; an empty text when found is false>", "note": "<what differs, when a place is not one that the \
plan gave or the content is not there as the element states it; when found is false, what stands now at the place \
that the plan gave; otherwise an empty text>"}}. Change nothing in the manuscript. Use no source other than the files in this folder.
'''

REMOVE_PROMPT = CONTEXT + '''

This session takes passages out of the manuscript. The running text of the paper was compared with the elements, and \
the passages listed in `removals.json` assert mathematics that no element states. One repair has already tried to cut \
or reword them, and they were still found afterwards. The paper is written from the research as it stands, and nothing \
is added to the library for the sake of a sentence, so these passages now leave the paper. No repair of the text \
follows this session, and the text is compared again only in a section whose LaTeX a later session has to correct. \
That is safe only because a deletion asserts nothing, and it is why this session deletes and does not reword.

In this folder:
- `removals.json` lists the passages. Each has its "number", the "part" it stands in, "where" it stands, "quote", the \
passage copied exactly from the manuscript, "asserts", what it asserts, and "nearest", the element that came nearest \
to stating it.
- `parts/` holds the parts of the manuscript, one file each. `paper.tex` is the manuscript assembled from them, for \
reading a passage where it stands. {spans}

For each entry, delete the quoted passage from its part. Then mend what stood around it so that the text reads on: \
close the sentence the passage was a clause of, remove a connective that now leads nowhere, such as "equivalently" or \
"in particular", and delete a later sentence that only refers back to what is gone. Where the quote is a displayed \
formula inside a proof, the fault is that text outside that proof refers to the formula as to a result: delete those \
references with the sentences that rest on them, and leave the formula in its proof.

Put nothing in the place of what you delete. Do not say the same thing in weaker or more careful words, and do not add \
a sentence that says what was removed or why. Leave every numbered statement exactly as it is, and change no passage \
that the list does not concern.

Write the complete new text of each part you change as `output/<name>.tex`, with the file name it has in `parts/`. The \
script accepts the output when no quoted passage stands in the running text any more, no formula of the list is \
referred to from outside its proof, every numbered statement is as it was, and every passage you changed is shorter \
than it was.
'''

RESTATE_PROMPT = CONTEXT + '''

This session restates numbered statements of the manuscript. Every numbered statement of the paper states one element \
of the research, and each was compared with the statement of its element. The statements listed in `statements.json` \
were found to differ from their elements, and they still differed after a repair. A statement of the paper may say \
nothing else than the library proves, so each of them is now restated as its element says it. One comparison follows \
this session and nothing after that: what you write is what the paper will state.

In this folder:
- `paper-method.md` is the method the manuscript was written by, here without its last two sections, which other \
sections name and which say what each session is given and how a manuscript is checked. It says what a numbered \
statement of the paper is and how it stands to its element.
- `statements.json` lists the statements. Each has its "label" and "number", the name of its "element", \
"record_statement", the statement of the element in words, "lean_statement", the same in Lean, "paper_statement", the \
statement as the manuscript has it, and "difference", what the comparison found.
- `records.md` holds the records of these elements in full. `elements/` holds the record of every element, one file \
each, and `elements.md` lists them.
- `parts/` holds the parts of the manuscript, one file each. `paper.tex` is the manuscript assembled from them. {spans}

For each entry, rewrite the statement so that it says exactly what its element states: the same objects, the same \
hypotheses, the same range of every variable, the same conclusion. Take the content from "record_statement", and where \
the words and the Lean statement differ, from "lean_statement", which is what was proved. Write it in the notation and \
the conventions of the manuscript, and keep the environment and its label. Say no more than the element and no less. \
Where the statement of the manuscript was stronger, more general or smoother than the element, the paper loses that, \
and "difference" names it.

Then bring the proof of that statement into agreement with it, so that it proves the statement as it now stands. \
Change nothing else: no other numbered statement, and no text outside the numbered statements and the proofs.

Write the complete new text of each part you change as `output/<name>.tex`, with the file name it has in `parts/`. The \
script accepts the output when each listed statement has another text than before, every other numbered statement has \
the text it had, and the text outside the statements and the proofs is unchanged.
'''


# ----------------------------------------------------------------------------- the run

def changed_materials(stored, fresh):
    """In what the materials on which the proof of the root rests now differ from those a run was started with;
    empty when in nothing.

    Compared are the root, the main result with the declaration that settles the root and the declarations of a
    draft ("main", "settles", "further"), the axioms, and the elements with their records. Nothing else is. The
    revision counts the publications of the instance, "identifiers" names every declaration and module of the
    instance, and the bibliography and the account of the problem as a whole belong to the whole research. A
    publication that changes nothing the proof of the root rests on can change each of these, and the run goes on
    with them as materials.json holds them, which is what a run that was not stopped does."""
    fresh = json.loads(json.dumps(fresh))
    found = [f'"{key}"' for key in ('root', 'main', 'settles', 'further', 'axioms', 'allowed_axioms')
             if stored.get(key) != fresh.get(key)]
    old, new = ({element['name']: element for element in materials['elements']} for materials in (stored, fresh))
    for words, names in (('elements that are no longer among them', [name for name in old if name not in new]),
                         ('new elements', [name for name in new if name not in old]),
                         ('elements whose record or standing changed', [name for name in old if name in new and old[name] != new[name]])):
        if names:
            found.append(f'{words}: ' + ', '.join(names[:10]) + (f' and {len(names) - 10} more' if len(names) > 10 else ''))
    if not found and list(old) != list(new):
        found.append('the order of the elements')
    return found


def same_canon(out, stored, fresh, lost):
    """Stop when the materials that the canon gives now are not those that the run in `out` was begun with.

    `lost` says, as a clause of the message, what cannot be done for that reason."""
    differing = changed_materials(stored, fresh)
    if differing:
        raise Stop(f'what the proof of the root rests on is no longer what {out / "materials.json"} holds, so the canon '
                   f'has changed since the run began, and {lost}; start a new run in a new folder. They differ in '
                   + '; '.join(differing))


def part_lines(text):
    """The lines of a part as `assemble` puts them into paper.tex."""
    return text.strip('\n').split('\n')


def written_parts(folder, names):
    """The texts of the parts among `names` that `folder` holds as <name>.tex, by name; an empty file is no part."""
    texts = {name: read_file(folder / (name + '.tex')) for name in names if (folder / (name + '.tex')).is_file()}
    return {name: text for name, text in texts.items() if text.strip()}


def changed_passages(before, after):
    """The passages in which two texts of one part differ, each as (i1, i2, j1, j2): the lines i1 to i2 - 1 of the
    text before became the lines j1 to j2 - 1 of the text after, counted from 0 in `part_lines`.

    A passage is a run of lines. Two runs of changed lines belong to one passage when no empty line stands in the
    unchanged lines between them, so that a passage never ends inside a paragraph: it can then be read, and put
    back as it was, by itself."""
    old, new = part_lines(before), part_lines(after)
    passages = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if tag == 'equal':
            continue
        if passages and all(line.strip() for line in new[passages[-1][3]:j1]):
            passages[-1] = (passages[-1][0], i2, passages[-1][2], j2)
        else:
            passages.append((i1, i2, j1, j2))
    return passages


def with_passages_undone(before, after, undone):
    """The text after, with the passages of `changed_passages` whose positions are in `undone` as they were before."""
    passages = changed_passages(before, after)
    if all(position in undone for position in range(len(passages))):
        return before
    old, new = part_lines(before), part_lines(after)
    lines, at = [], 0
    for position, (i1, i2, j1, j2) in enumerate(passages):
        lines += new[at:j1] + (old[i1:i2] if position in undone else new[j1:j2])
        at = j2
    return '\n'.join(lines + new[at:]) + '\n'


def chosen_numbers(text, count):
    """The numbers that --open-findings was given, as in "2,5-7"; every number of the list for "all"."""
    if text == 'all':
        return list(range(1, count + 1))
    numbers = set()
    for piece in text.split(','):
        match = re.fullmatch(r'\s*(\d+)\s*(?:-\s*(\d+)\s*)?', piece)
        if not match:
            raise Stop(f'--open-findings takes the numbers of the findings as its dry run lists them, such as 2,5-7, or '
                       f'nothing for all of them; it was given "{text}". The instance comes before the options')
        first, last = int(match[1]), int(match[2] or match[1])
        if not 1 <= first <= last <= count:
            raise Stop(f'--open-findings {text}: the run has {count} open findings, numbered from 1 to {count}')
        numbers.update(range(first, last + 1))
    return sorted(numbers)


def size(files, wanted=lambda name: True):
    """The bytes of the files of a session whose names `wanted` accepts."""
    return sum(len(text if isinstance(text, bytes) else text.encode('utf-8')) for name, text in files.items() if wanted(name))


def answered_each(response, count, actions=('revised', 'kept')):
    """Whether a response answers each of `count` findings: an object with an "action" among `actions` and a "note"."""
    return len(response) == count and all(isinstance(r, dict) and r.get('action') in actions and is_text(r.get('note'))
                                          for r in response)


def read_draft(folder):
    """The plan, the account of the papers and the draft that a folder holds for --from-draft; stops when it holds none."""
    folder = Path(folder)
    missing = [name for name in ('plan.json', 'study.md', 'draft.json') if not (folder / name).is_file()]
    if missing:
        raise Stop(f'{folder} holds no draft of this command to write the paper from: it has no ' + ', '.join(missing))
    try:
        plan, draft = (json.loads(read_file(folder / name)) for name in ('plan.json', 'draft.json'))
    except ValueError as exc:
        raise Stop(f'the draft in {folder} cannot be read: plan.json or draft.json is not JSON ({exc})')
    study = read_file(folder / 'study.md')
    lists = lambda holder, keys: isinstance(holder, dict) and all(
        isinstance(holder.get(key), list) and all(isinstance(entry, dict) for entry in holder[key]) for key in keys)
    if not lists(plan, ('sections', 'statements', 'others')) or not lists(draft, ('statements', 'formulas', 'gaps')) \
            or not study.strip():
        raise Stop(f'the draft in {folder} does not have the form of a draft of this command: plan.json with "sections", '
                   '"statements" and "others", draft.json with "statements", "formulas" and "gaps", each an array of '
                   'objects, and a study.md that is not empty')
    # Two lists that whoever brought the draft to the library may have added: the results that are an instance of
    # a cited general theorem (instance_lines), and what the cited works say at the places the records cite
    # (Paper.cover_section). Each is optional, and each has a fixed form.
    for key, fields in (('instances', ('element', 'key', 'where', 'states', 'specialisation')),
                        ('attributions', ('key', 'declaration', 'sentence', 'place', 'quote'))):
        if not all(isinstance(entry, dict) and all(is_text(entry.get(field)) for field in fields)
                   for entry in draft.get(key) or []) or not isinstance(draft.get(key) or [], list):
            raise Stop(f'the draft in {folder}: "{key}" in draft.json, when it is there, is an array of objects, each with '
                       + ', '.join(f'"{field}"' for field in fields) + ' as texts that are not empty')
    return plan, study, draft


def carried_plan(materials, plan, draft):
    """The plan of a draft carried over to the materials as they are now, and what was changed in it, as sentences.

    Between the draft and the paper the library changed: declarations were added to close the gaps of
    the draft, others were renamed or removed, and sources were entered into records. The draft says,
    for each statement, which element states it now, and for each gap which declaration closed it.
    The script does what follows from that without a decision. An element that is no longer among the
    materials leaves the plan, and so does a statement that the draft marks as cut. A statement that
    another declaration now states names that declaration, under its kind and label. The element it
    named before is recorded as not stated, with the new one in its place, when its proof names the
    new one; otherwise it is absorbed into the numbered statements that name it, since the paper no
    longer states it and their proofs still use it. A declaration that closed a gap of a formula or of
    an assertion is absorbed where the gap stood: into the numbered statement in whose proof the gap
    stood when that statement's element rests on the declaration, and otherwise into the running text
    of the gap's section. A statement whose element now has a source is cited, and one whose element
    lost its source is proved again. The materials of such a paper hold the declarations that closed
    a gap also where the proof of the root does not use them (extract). Whatever this leaves wrong,
    such as an element that the library gained and the plan does not mention, the check of the plan
    reports."""
    elements = {element['name']: element for element in materials['elements']}
    plan = json.loads(json.dumps(plan))
    notes, statements, renamed = [], [], {}
    drafted = {entry.get('label'): entry for entry in draft['statements']}
    gaps = {gap.get('id'): gap for gap in draft['gaps']}
    for item in plan['statements']:
        label, before = item.get('label'), item.get('element')
        entry = drafted.get(label, {})
        if entry.get('cut'):
            notes.append(f'the statement `{label}` was cut from the draft and is no numbered statement any more')
            continue
        name = gaps.get(entry.get('gap'), {}).get('closed_by') or entry.get('element') or before
        if name not in elements:
            notes.append(f'the statement `{label}` left the plan: its element `{name}` is not among the materials')
            continue
        if name != before:
            renamed[before] = name
            notes.append(f'the statement `{label}` states `{name}`, where the draft had `{before}`')
            item['element'] = name
        if elements[name]['kind'] == 'statement':
            if elements[name]['source'] and item.get('proof') != 'cited':
                item['proof'] = 'cited'
                notes.append(f"the statement `{label}` is cited and not proved: the record of `{name}` names the source "
                             f"`{elements[name]['source']}`")
            elif not elements[name]['source'] and item.get('proof') == 'cited':
                del item['proof']
                notes.append(f'the statement `{label}` is proved where it is stated: the record of `{name}` names no '
                             'source any more')
        statements.append(item)
    placed = {item['element'] for item in statements}
    ids = [section.get('id') for section in plan['sections']]
    others = []
    for item in plan['others']:
        name = item.get('element')
        if name not in elements:
            notes.append(f'`{name}` left the plan: it is not among the materials')
            continue
        if name in placed:
            continue
        if isinstance(item.get('into'), list):
            into = [renamed.get(target, target) for target in item['into']]
            item['into'] = list(dict.fromkeys(target for target in into if target in ids or target in placed))
        if item.get('by') in renamed:
            item['by'] = renamed[item['by']]
        others.append(item)
        placed.add(name)
    for before, name in renamed.items():
        if before not in elements or before in placed:
            continue
        if stands_in(elements[before], elements[name], elements):
            others.append({'element': before, 'treatment': 'not_stated', 'by': name,
                           'reason': 'The paper states this result in the form of the element under "by", which the '
                                     'library gained after the draft; this element is the form it had before.'})
            notes.append(f'`{before}` is not stated: `{name}` stands in its place')
        else:
            # The proof of the old form does not name the new one, so the new one cannot stand for it in the plan.
            users = [item['element'] for item in statements
                     if before in elements[item['element']]['uses'] + elements[item['element']]['mentions']]
            if not users:
                notes.append(f'`{before}` has no place in the plan: `{name}` is stated where it was, its own proof does '
                             f'not name `{name}`, and no numbered statement names it')
                continue
            others.append({'element': before, 'treatment': 'absorbed', 'into': users,
                           'reason': 'The paper states, under the label this element had, the form that the library '
                                     'gained after the draft; this form is written where a proof uses it.'})
            notes.append(f'`{before}` is absorbed into ' + ', '.join(f'`{user}`' for user in users)
                         + f': `{name}` is stated where it was')
        placed.add(before)
    hosts = {item['label']: item['element'] for item in statements}
    for gap in draft['gaps']:
        name = gap.get('closed_by')
        if gap.get('kind') == 'statement' or name not in elements or name in placed:
            continue
        # Into the statement in whose proof the gap stood, when its element rests on the declaration, so that
        # the check of the plan accepts it; otherwise into the running text of the section of the gap.
        host = hosts.get(gap.get('host'))
        target = host if host and rests_on(elements, host, name) else gap.get('section') if gap.get('section') in ids else None
        if target is None:
            notes.append(f"`{name}`, which closed the gap {gap.get('id')}, has no place in the plan: the section of the "
                         'gap is gone')
            continue
        others.append({'element': name, 'treatment': 'absorbed', 'into': [target],
                       'reason': 'It states what the draft of the paper needed at this place and the library did not '
                                 'yet contain.'})
        placed.add(name)
        notes.append(f"`{name}`, which closed the gap {gap.get('id')}, is absorbed into `{target}`")
    plan['statements'], plan['others'] = statements, others
    for entry in plan.get('notation') or []:
        if isinstance(entry, dict) and isinstance(entry.get('elements'), list):
            entry['elements'] = [renamed.get(name, name) for name in entry['elements'] if renamed.get(name, name) in elements]
    if isinstance(plan.get('citations'), list):
        plan['citations'] = [entry for entry in plan['citations'] if isinstance(entry, dict)
                             and entry.get('element') in elements and not elements[entry['element']]['source']]
    if isinstance(plan.get('displays'), list):
        # A formula that several sections use names the element that states it now, and leaves with that element.
        named = lambda entry: renamed.get(entry.get('element'), entry.get('element')) if isinstance(entry, dict) else None
        plan['displays'] = [{**entry, 'element': named(entry)} for entry in plan['displays'] if named(entry) in elements]
    return plan, notes


def judged_in_order(verdicts, labels):
    """Whether a comparison gives one verdict for each of `labels`, in their order: "same", or "differs" with the difference."""
    return ([v.get('label') if isinstance(v, dict) else None for v in verdicts] == labels
            and all(v.get('verdict') in ('same', 'differs') for v in verdicts)
            and all(is_text(v.get('difference')) for v in verdicts if v['verdict'] == 'differs'))


class Paper(Sessions):
    """One run of the command: its folder, what it was given, what the sessions made, and the log."""

    def __init__(self, instance, out, tex, choice, parallel=PARALLEL, dry=False, gate=None):
        super().__init__(instance, out, parallel, dry, gate)
        chosen = {'model': choice.get('model') or self.writer['model'], 'effort': choice.get('effort') or self.writer['effort']}
        # The readings and the comparison come, where the settings name one, from the model that reviews.
        self.writer = chosen
        if choice.get('model'):
            self.assessor = chosen
        # A model that names no provider, or an effort that its CLI does not take, is refused here, before the run
        # has written anything; a session would fail on it only when the folder of the run is already begun.
        for each in (self.writer, self.assessor):
            build_command(self.settings['cli'][provider_for_model(each['model'])], each['model'], each['effort'], self.out)
        self.recipe = tex_recipe(tex)
        # The authors of the title page; a run keeps the file it was given as <out>/title-page.json.
        self.authors = read_title_page(self.out / 'title-page.json') if (self.out / 'title-page.json').is_file() else []
        # The codes of the subject classification, which the same file gives; none without it.
        self.codes = read_classification(self.out / 'title-page.json') if (self.out / 'title-page.json').is_file() else []
        self.materials = self.plan = self.layout = self.research = None
        self.parts, self.compared, self.open = {}, {}, []
        # What the readings found and the stage `resolve` or the last narrow repair answered with a reason: each
        # with its check, the finding and the reason. It is listed at the end of the run and is not open.
        self.kept = []
        # What a run left open and `close` then closed without a person: each passage that was taken out, each
        # statement that was restated, and what is recorded and left as it is. The `end` event carries it.
        self.closed = []
        # Where the manuscript has the elements without a number, as the last check of it found (place): the
        # digest of the text that was checked, and for each element whether and where it was found.
        self.placed = None
        # The stage `resolve` while it is under way: its step, the findings it took up and the answers of its
        # session (resolve). None when it is not under way.
        self.resolving = None
        # The draft that the paper is written from (--from-draft): its statements, formulas and gaps. None otherwise.
        self.sketched = None
        # A narrow repair that is under way, with the reading of what it changed: its step, the findings it takes
        # up, and what its later steps need of the earlier ones (narrow_begin). None when none is under way.
        self.narrow = None
        # How often the manuscript was read by itself, and whether a repair that followed a reading beside real
        # papers or a comparison has changed a part since it was last read in that way (read_again).
        self.readings, self.rewritten = 0, False
        # The stages after the writing that are complete, each with whether the run goes on after it.
        self.done = {}
        # The collection of real papers and the planning session's account of how the chosen ones are
        # written; --typeset-only has neither.
        self.collection, self.papers, self.study = None, {}, None

    def save(self):
        """state.json: how far the stages after the writing have come, and what the later ones need of the earlier."""
        with self.lock:
            if not self.dry:
                write_json(self.out / 'state.json', {'done': self.done, 'open': self.open, 'readings': self.readings,
                                                     'rewritten': self.rewritten, 'compared': self.compared,
                                                     'narrow': self.narrow, 'kept': self.kept,
                                                     'closed': self.closed, 'resolve': self.resolving,
                                                     'placed': self.placed})

    # -- what a session is given ------------------------------------------------------------------------

    def records(self):
        """root.md, elements.md, elements/ and references.bib, for a session that works from the records."""
        if self.research is None:
            self.research = {**record_files(self.materials), 'references.bib': self.materials['bibliography']}
        return self.research

    def plan_text(self):
        return json.dumps(self.plan, ensure_ascii=False, indent=2) + '\n'

    def section_papers(self, section):
        """The papers the plan names for a section, when there is a collection to take them from."""
        return list(section.get('exemplars') or []) if self.collection is not None else []

    def planning_kit(self):
        """The files of the session that plans: the digest, the record of every element, and the whole collection."""
        return {'paper-method.md': method_before_checks(), 'user-writing-preferences.md': read_file(PREFERENCES),
                'materials-digest.md': render_digest(self.materials),
                **{name: text for name, text in self.records().items() if name.startswith('elements/')},
                'exemplars.md': render_exemplars(self.collection),
                **{f'exemplars/{key}.tex': text for key, text in self.papers.items()}}

    def kit(self, section):
        """The files of a session that writes or repairs one section: its brief, the records, the account of the
        chosen papers and the papers the plan names for the section."""
        files = {'paper-method.md': method_before_checks(), 'user-writing-preferences.md': read_file(PREFERENCES),
                 'brief.md': render_brief(self.materials, self.plan, section, self.layout, self.sketched),
                 'plan.json': self.plan_text(), **self.records()}
        if self.collection is not None:
            files['study.md'] = self.study
            files.update({f'exemplars/{key}.tex': self.papers[key] for key in self.section_papers(section)})
        return files

    def research_note(self, section=None):
        """What the prompt says of root.md and of elements/, for the session of one section or of the whole."""
        if section is None:
            return {'root': 'The paper uses the conventions of the root as it is stated in words.', 'elements': ELEMENTS_WHOLE}
        return {'root': ROOT_FIRST if section is self.plan['sections'][0] else ROOT_LATER, 'elements': ELEMENTS_SECTION}

    # -- stages -----------------------------------------------------------------------------------------

    def take_plan(self, plan, study):
        self.plan, self.study = plan, study
        self.layout = Layout(self.materials, plan)

    def keys(self):
        """The keys of the collection, from which a plan chooses its papers."""
        return [entry['key'] for entry in self.collection]

    def make_plan(self, draft=False):
        """The planning session. For a draft it is also asked for the results the paper would cite (PLAN_CITATIONS)."""
        def read(output):
            plan = self.load(output / 'plan.json')
            problems = check_plan(self.materials, plan, self.keys())
            if draft and not isinstance(plan.get('citations'), list):
                problems.append('"citations" is an array, empty when the paper would cite no result whose record names '
                                'no source')
            # The account is passed on as it is; that it exists and is not empty is all the script checks.
            study = read_file(output / 'study.md') if (output / 'study.md').is_file() else ''
            if not study.strip():
                problems.append('output/study.md, the account of how the chosen papers are written, was not written '
                                'or is empty')
            if problems:
                raise Unusable(problems)
            return plan, study

        # Only the plan of a draft is asked for the results to cite, and the note on the main result is empty when the
        # declaration that settles the root is the main result.
        prompt = (PLAN_OPENING + PLAN_KEYS + (PLAN_CITATIONS if draft else '') + PLAN_ACCEPTS
                  + main_note(self.materials) + PLAN_CLOSING)
        self.take_plan(*self.session('plan', prompt, self.planning_kit(), read,
                                     self.writer, attempts=PLAN_ATTEMPTS))
        self.keep_plan()

    def keep_plan(self, **more):
        """The plan and its account, into <out>, and the event that says what the plan holds."""
        write_text(self.out / 'study.md', self.study)  # the account first: a plan in the folder has its account beside it
        write_json(self.out / 'plan.json', self.plan)
        self.event('plan', statements=len(self.plan['statements']), sections=[s['id'] for s in self.plan['sections']],
                   exemplars=self.plan['exemplars'], papers={s['id']: s['exemplars'] for s in self.plan['sections']},
                   notation=len(self.plan['notation']), **more)

    def plan_from_draft(self, folder):
        """The plan of a draft, brought to the materials of this instance; a session repairs it only when it fails.

        The script carries the plan over (carried_plan) and the check of the plan decides. When the check
        finds problems, a planning session receives the plan, what the script changed, the problems, the
        account of the papers and the drafted statements, and returns a plan, within the bound of the
        planning sessions. It is given no paper of the collection: the papers were read for the draft."""
        plan, study, draft = read_draft(folder)
        draft = self.sketched or draft  # the draft as the run recorded it when it began, from which its materials are
        carried, notes = carried_plan(self.materials, plan, draft)
        problems = check_plan(self.materials, carried, self.keys())
        self.event('check', check='the plan of the draft, brought to the materials', changes=notes, problems=problems)
        if problems:
            def read(output):
                repaired = self.load(output / 'plan.json')
                found = check_plan(self.materials, repaired, self.keys())
                if not found and (repaired.get('exemplars') != carried['exemplars']):
                    found.append('"exemplars" stays as plan.json has it: the papers were chosen and read for the draft, '
                                 'and study.md is the account of those papers')
                if found:
                    raise Unusable(found)
                return repaired

            files = {'paper-method.md': method_before_checks(), 'materials-digest.md': render_digest(self.materials),
                     **{name: text for name, text in self.records().items() if name.startswith('elements/')},
                     'plan.json': json.dumps(carried, ensure_ascii=False, indent=2) + '\n', 'study.md': study,
                     'carried.md': '\n'.join(['# What the script changed in the plan of the draft', '',
                                              *(['- ' + note for note in notes] or ['Nothing.'])]) + '\n',
                     'problems.md': '\n'.join(['# What the check of the plan found', '',
                                               *('- ' + problem for problem in problems)]) + '\n',
                     'draft.json': json.dumps(draft, ensure_ascii=False, indent=2) + '\n'}
            prompt = PLAN_REPAIR_PROMPT.format(plan_keys=PLAN_KEYS + PLAN_ACCEPTS + main_note(self.materials))
            carried = self.session('plan', prompt, files, read, self.writer, 'from-draft', attempts=PLAN_ATTEMPTS)
        self.take_plan(carried, study)
        self.sketched = draft
        write_json(self.out / 'draft.json', draft)
        self.keep_plan(from_draft=True, carried=notes, repaired=bool(problems))

    # -- the draft --------------------------------------------------------------------------------------

    def sketch_section(self, section):
        """The sketch of one section: the session that makes it, or the sketch that <out>/sketch already holds."""
        kept = self.out / 'sketch' / (section['id'] + '.json')
        if kept.is_file():
            return read_json(kept)
        sid, elements = section['id'], self.layout.elements
        stated = [item for item in self.plan['statements'] if item['section'] == sid]
        hosts = {item['label'] for item in self.plan['statements']
                 if item['section'] == sid or self.layout.proof_of(item) == sid}

        def gap_problems(where, gap, nearest):
            if not isinstance(gap, dict) or not all(is_text(gap.get(key)) for key in ('wanted', 'has', 'reason')):
                return [f'{where}: a gap is an object with "wanted", "has" and "reason", each a text that is not empty']
            if nearest and gap.get('element') not in elements:
                return [f'{where}: "element" of the gap is the name of the element of the materials that comes nearest']
            return []

        def read(output):
            sketch = self.load(output / 'sketch.json')
            problems = []
            statements, formulas, assertions = (sketch.get(key) for key in ('statements', 'formulas', 'assertions'))
            for key, value in (('statements', statements), ('formulas', formulas), ('assertions', assertions)):
                if not isinstance(value, list) or not all(isinstance(entry, dict) for entry in value):
                    raise Unusable([f'output/sketch.json: "{key}" is an array of objects, empty when there is none'])
            if [entry.get('label') for entry in statements] != [item['label'] for item in stated]:
                problems.append('"statements" has one object for each numbered statement that the plan has this section '
                                'state, in the order of the plan: ' + (', '.join(item['label'] for item in stated) or 'none'))
            for entry in statements:
                where = f"statement {entry.get('label')}"
                if not is_text(entry.get('text')):
                    problems.append(f'{where}: "text" is the statement as the paper will have it')
                if entry.get('gap') is not None:
                    problems += gap_problems(where, entry['gap'], False)
            labels = set()
            for entry in formulas:
                label = entry.get('label')
                where = f'formula {label}'
                if not (isinstance(label, str) and LABEL_FORM.fullmatch(label) and label.startswith(f'eq:{sid}-')
                        and label not in labels):
                    problems.append(f'{where}: "label" is eq:{sid}- followed by lowercase letters, digits and hyphens, '
                                    'and is used once')
                labels.add(label)
                if not is_text(entry.get('text')):
                    problems.append(f'{where}: "text" is the formula as it will be displayed')
                if entry.get('host') is not None and entry['host'] not in hosts:
                    problems.append(f'{where}: "host" is null or the label of a numbered statement that this section '
                                    'states or proves')
                if (entry.get('element') is None) == (entry.get('gap') is None):
                    problems.append(f'{where}: either "element" names the element that states the formula and "gap" is '
                                    'null, or "element" is null and "gap" says what is wanted')
                elif entry.get('element') is not None and entry['element'] not in elements:
                    problems.append(f"{where}: {entry['element']!r} is not an element of the materials")
                elif entry.get('gap') is not None:
                    problems += gap_problems(where, entry['gap'], True)
            for number, entry in enumerate(assertions, 1):
                where = f'assertion {number}'
                if entry.get('host') is not None and entry['host'] not in hosts:
                    problems.append(f'{where}: "host" is null or the label of a numbered statement that this section '
                                    'states or proves')
                problems += gap_problems(where, entry, True)
            if problems:
                raise Unusable(['output/sketch.json: ' + problem for problem in problems])
            return {'statements': [{'label': e['label'], 'text': e['text'].strip(), 'gap': e.get('gap')} for e in statements],
                    'formulas': [{'label': e['label'], 'host': e.get('host'), 'text': e['text'].strip(),
                                  'element': e.get('element'), 'gap': e.get('gap')} for e in formulas],
                    'assertions': [{key: e.get(key) for key in ('host', 'element', 'wanted', 'has', 'reason')}
                                   for e in assertions]}

        papers = self.section_papers(section)
        first = section is self.plan['sections'][0]
        prompt = SKETCH_PROMPT.format(
            id=sid, title=section['title'], content=section['content'], count=len(papers),
            also=' As the first section it is the introduction; the abstract is not sketched.' if first else '',
            papers=' and '.join(f'`exemplars/{key}.tex`' for key in papers), **self.research_note(section))
        # A sketch has no prose, so the session is given what a writer is given except the writing preferences.
        files = {name: text for name, text in self.kit(section).items() if name != 'user-writing-preferences.md'}
        sketch = self.session('sketch', prompt, files, read, self.writer, sid)
        write_json(kept, sketch)
        return sketch

    def compare_sketch(self, section, sketch):
        """The verdicts on the sketched statements of one section, and on its formulas that name an element.

        They come from one comparison session, or from <out>/sketch when the session was already made;
        a section that has nothing to compare has no session."""
        kept = self.out / 'sketch' / (section['id'] + '.compared.json')
        if kept.is_file():
            return read_json(kept)
        elements = self.layout.elements
        states = {item['label']: item['element'] for item in self.plan['statements']}
        rows = [{'label': entry['label'], 'kind': 'numbered statement', 'element': states[entry['label']],
                 'draft_statement': entry['text'], 'declared_gap': entry['gap']} for entry in sketch['statements']]
        rows += [{'label': entry['label'], 'kind': 'displayed formula', 'element': entry['element'],
                  'draft_statement': entry['text'], 'declared_gap': None} for entry in sketch['formulas'] if entry['element']]
        for row in rows:
            element = elements[row['element']]
            row.update(record_statement=element['statement'], lean_statement=element['lean'])
        verdicts = []
        if rows:
            labels = [row['label'] for row in rows]
            slips = {row['label'] for row in rows if row['declared_gap'] is None}

            def read(output):
                found = self.load(output / 'comparison.json', list)
                if not judged_in_order(found, labels) \
                        or not all(is_text(v.get('text')) for v in found
                                   if v['verdict'] == 'differs' and v['label'] in slips and v.get('partial') is not True):
                    raise Unusable(['output/comparison.json has one object for each entry of statements.json, in their '
                                    'order, with its "label", a "verdict" of "same" or "differs", for "differs" the '
                                    '"difference", and for an entry without a declared gap that differs, unless it is '
                                    'partial, the "text": the statement as the element says it'])
                return [{'label': v['label'], 'verdict': v['verdict'], 'difference': v.get('difference') or '',
                         'text': v['text'].strip() if is_text(v.get('text')) else '',
                         'partial': v['verdict'] == 'differs' and v['label'] in slips and v.get('partial') is True,
                         'record_disagreement': v['record_disagreement'] if is_text(v.get('record_disagreement')) else ''}
                        for v in found]

            files = {'paper-method.md': method_before_checks(), 'plan.json': self.plan_text(),
                     'statements.json': json.dumps(rows, ensure_ascii=False, indent=2) + '\n',
                     'records.md': render_records(self.materials, self.plan, {row['element'] for row in rows}, self.layout),
                     **{name: text for name, text in self.records().items() if name.startswith('elements')}}
            verdicts = self.session('compare', DRAFT_COMPARE_PROMPT.format(title=section['title']), files, read,
                                    self.assessor, section['id'],
                                    check={None: 'the comparison of the drafted statements and formulas of the section "'
                                                 + collapsed(section['title']) + '" with their elements'})
            if verdicts is None:
                # Not made (session): the sketch stands as it was sketched, and the comparisons after the draft and
                # of the paper are the ones that judge these texts.
                return []
        write_json(kept, verdicts)
        return verdicts

    def draft(self):
        """The draft of the paper, from the plan: draft.json in <out>, and the end of the run; returns the exit code.

        For each section a session sketches the statements, the formulas that are used as results and
        the gaps, the sections side by side. Sessions then compare what was sketched with the elements.
        A statement or a formula that differs from its element is a gap the sketch declared, which
        stays, or a slip, which is replaced by the text the comparison gives. A gap that the
        comparison finds to be none is dropped. Every sketch and every list of verdicts is kept in
        <out>/sketch when it is accepted, so a run that was stopped does not make it again."""
        sections = self.plan['sections']
        (self.out / 'sketch').mkdir(exist_ok=True)
        sketches = self.side_by_side([lambda section=section: self.sketch_section(section) for section in sections])
        compared = self.side_by_side([lambda section=section, sketch=sketch: self.compare_sketch(section, sketch)
                                      for section, sketch in zip(sections, sketches)])
        states = {item['label']: item['element'] for item in self.plan['statements']}
        draft = {'statements': [], 'formulas': [], 'gaps': [],
                 'citations': [{key: entry.get(key) for key in ('element', 'result', 'reason')}
                               for entry in self.plan.get('citations', [])],
                 # The draft records the main result it was made around when that is not the settling declaration,
                 # so that the paper is written from it around the same theorem.
                 **({'main': self.materials['main']} if 'settles' in self.materials else {})}
        slips, dropped, disagreements, trimmed = [], [], [], []

        def gap(kind, section, label, host, element, said):
            draft['gaps'].append({'id': f"g{len(draft['gaps']) + 1}", 'kind': kind, 'section': section, 'label': label,
                                  'host': host, 'element': element, 'wanted': said['wanted'], 'has': said['has'],
                                  'reason': said['reason'], 'closed_by': None})
            return draft['gaps'][-1]['id']

        for section, sketch, verdicts in zip(sections, sketches, compared):
            sid, judged = section['id'], {verdict['label']: verdict for verdict in verdicts}
            disagreements += [{'label': label, 'record_disagreement': verdict['record_disagreement']}
                              for label, verdict in judged.items() if verdict['record_disagreement']]
            for kind, entries in (('statement', sketch['statements']), ('formula', sketch['formulas'])):
                for entry in entries:
                    verdict, text, said = judged.get(entry['label']), entry['text'], entry['gap']
                    if verdict and verdict['verdict'] == 'differs' and said is None and verdict.get('partial'):
                        # The text states some of the parts of its element and nothing else. It stays, as a gap
                        # that a declaration of those parts alone closes.
                        said = {'element': entry.get('element'), 'wanted': text, 'has': verdict['difference'],
                                'reason': PARTIAL}
                        trimmed.append(entry['label'])
                    elif verdict and verdict['verdict'] == 'differs' and said is None:
                        slips.append({'label': entry['label'], 'difference': verdict['difference']})
                        text = verdict['text']
                    elif verdict and verdict['verdict'] == 'same' and said is not None:
                        dropped.append(entry['label'])
                        said = None
                    if kind == 'statement':
                        element = states[entry['label']]
                        draft['statements'].append({
                            'label': entry['label'], 'section': sid, 'element': element, 'text': text,
                            'gap': gap('statement', sid, entry['label'], None, element, said) if said else None})
                    else:
                        draft['formulas'].append({
                            'label': entry['label'], 'section': sid, 'host': entry['host'], 'text': text,
                            'element': entry['element'],
                            'gap': gap('formula', sid, entry['label'], entry['host'], said['element'], said) if said else None})
            for entry in sketch['assertions']:
                gap('assertion', sid, None, entry['host'], entry['element'], entry)
        write_json(self.out / 'draft.json', draft)
        self.event('draft', statements=len(draft['statements']), formulas=len(draft['formulas']),
                   gaps=[{key: entry[key] for key in ('id', 'kind', 'section', 'label', 'element')} for entry in draft['gaps']],
                   citations=[entry['element'] for entry in draft['citations']], slips=slips, gaps_dropped=dropped,
                   partial=trimmed, record_disagreements=disagreements)
        self.event('end', status='draft', open=[], kept=[], **({'not_done': list(self.undone)} if self.undone else {}))
        print(f'The draft is {self.out / "draft.json"}, beside the plan and the account of the papers (plan.json, '
              f'study.md); the log is {self.out / "log.json"}.')
        for line in not_done_lines(self.undone):
            print(line)
        print(f"{len(draft['statements'])} statements and {len(draft['formulas'])} formulas were drafted; "
              f"{len(draft['gaps'])} gaps and {len(draft['citations'])} results to cite are listed.")
        return 0

    def written(self, section):
        """Whether a section is written; the introduction is written with the abstract."""
        return section['id'] in self.parts and (section is not self.plan['sections'][0] or 'abstract' in self.parts)

    def write_parts(self):
        """The sections that are not written yet: the introduction first and alone, the others side by side.

        The introduction defines the objects of the problem and states the main result, so every other
        writer is given it. The other sections rest on the plan alone and are written in any order."""
        sections = self.plan['sections']
        todo = [section for section in sections if not self.written(section)]
        if todo and todo[0] is sections[0]:
            self.write_section(todo.pop(0))
        self.side_by_side([lambda section=section: self.write_section(section) for section in todo])

    def write_section(self, section):
        sections = self.plan['sections']
        first = section is sections[0]
        names = [section['id']] + (['abstract'] if first else [])

        def read(output):
            written = written_parts(output, names)
            missing = [f'output/{name}.tex was not written or is empty' for name in names if name not in written]
            if missing:
                raise Unusable(missing)
            return written

        with self.lock:  # the parts that are finished now; a part that is finished later is not seen by this session
            finished = {other['id']: self.parts[other['id']] for other in sections if self.written(other)}
            if finished and 'abstract' in self.parts:
                finished['abstract'] = self.parts['abstract']
        held = [f"`parts/{other['id']}.tex`"
                + (' with `parts/abstract.tex` (the introduction and the abstract)' if other is sections[0]
                   else f" (Section {number}, \"{other['title'].strip()}\")")
                for number, other in enumerate(sections, 1) if other['id'] in finished]
        others = any(other['id'] not in finished and other is not section for other in sections)
        papers = self.section_papers(section)
        prompt = WRITE_PROMPT.format(
            id=section['id'], title=section['title'], content=section['content'],
            also=' As the first section it is the introduction, and this session also writes the abstract.' if first else '',
            order=(ORDER_AGAIN if finished else ORDER_FIRST) if first else ORDER_LATER, **self.research_note(section),
            drafted=DRAFTED if self.sketched and drafted_lines(self.plan, section, self.sketched) else '',
            parts=PARTS.format(held=', '.join(held), others=PARTS_OTHERS if others else '') if finished else NO_PARTS,
            count=len(papers), papers=' and '.join(f'`exemplars/{key}.tex`' for key in papers),
            abstract=(' Write also `output/abstract.tex`: the text of the abstract, without the abstract '
                      'environment.') if first else '')
        files = {**self.kit(section), **{f'parts/{name}.tex': text for name, text in finished.items()}}
        self.keep(self.session('write', prompt, files, read, self.writer, section['id']))

    def keep(self, parts):
        """Take the new text of parts, in memory and in <out>/parts; the abstract before the introduction it came with."""
        with self.lock:
            for name in sorted(parts, key=lambda name: name != 'abstract'):
                (self.out / 'parts').mkdir(exist_ok=True)
                write_text(self.out / 'parts' / (name + '.tex'), parts[name])
                self.parts[name] = parts[name]

    def assemble(self):
        """paper.tex, references.bib and the correspondence file from the parts as they stand."""
        tex, spans = assemble(self.plan, self.parts, self.authors, self.codes)
        write_text(self.out / 'paper.tex', tex)
        write_text(self.out / 'references.bib', capitals_kept(self.materials['bibliography']))
        elements = {e['name']: e for e in self.materials['elements']}
        by_label = {item['label']: item for item in self.plan['statements']}
        rows, instances = [], self.instances()
        for found in found_statements(self.plan, self.parts):
            if found['label'] not in by_label:
                continue  # the machine check reports it
            element = elements[by_label[found['label']]['element']]
            digest = sha256_text(found['text'])
            judged = self.compared.get(found['label'])
            # A statement that the paper cites and does not prove is proved in the library all the same, as every
            # element here is. The paper does not say so; this file does, by naming the source the paper cites.
            cited = element['source'] if self.layout.proof_of(by_label[found['label']]) == 'cited' else None
            # A statement that the paper proves from a cited general theorem, by a specialisation, names the theorem.
            instance = next((entry for entry in instances if entry['label'] == found['label']), None)
            rows.append({'number': f"{found['kind'].capitalize()} {found['number']}", 'label': found['label'],
                         'element': element['name'], 'states': element['states'] or element['name'], 'cited': cited,
                         **({'instance_of': {'key': instance['key'], 'where': instance['where']}} if instance else {}),
                         'record_statement': element['statement'], 'record_statement_from': element['statement_from'],
                         'lean_statement': element['lean'], 'paper_statement': found['text'],
                         'paper_statement_sha256': digest,
                         'comparison': ({'verdict': judged['verdict'], 'difference': judged['difference'],
                                         'record_disagreement': judged['record_disagreement']}
                                        if judged and judged['sha256'] == digest else {'verdict': 'not compared'})})
        # A comparison that was not made (session) is recorded for a statement as long as its present text has no
        # verdict; the row then says why it has none.
        pending = {row['label'] for row in rows if row['comparison']['verdict'] == 'not compared'}
        with self.lock:
            kept = [entry for entry in self.undone
                    if entry['kind'] != 'compare' or entry['about'] is None or entry['about'] in pending]
            if kept != self.undone:
                self.undone = kept
                if not self.dry:
                    write_json(self.out / 'not-done.json', self.undone)
            stopped = {entry['about']: entry for entry in self.undone if entry['kind'] == 'compare'}
        for row in rows:
            if row['label'] in stopped and row['label'] in pending:
                row['comparison']['not_done'] = not_done_lines([stopped[row['label']]])[0]
        # An element without a number carries, under "in_text", what the check of the manuscript found of it
        # (place), as long as the manuscript is the text that was checked.
        found = (self.placed or {}).get('found') if (self.placed or {}).get('digest') == self.text_digest() else None
        write_json(self.out / 'correspondence.json', {
            'root': self.materials['root']['name'], 'main_result': self.materials['main'],
            **({'settled_by': self.materials['settles']} if 'settles' in self.materials else {}),
            'revision': self.materials['revision'], 'statements': rows,
            'others': [{**item, **({'in_text': found[item['element']]} if found and item['element'] in found else {})}
                       for item in self.plan['others']],
            # The elements that the paper takes from a cited general theorem by a specialisation, numbered or not.
            # The library proves each of them by itself; the paper does not say so, and this file does.
            'instances': [{key: entry[key] for key in ('element', 'key', 'where')}
                          for entry in (self.sketched or {}).get('instances') or []
                          if entry['key'] in self.materials['bibliography_keys'] and entry['element'] in elements],
            # The checks of this run that were not made, each in a sentence; an empty list when every one was made.
            'not_done': not_done_lines(self.undone)})
        return tex, spans, rows

    def settle(self, rounds=REPAIR_ROUNDS):
        """Assemble, check by machine and typeset, with repair sessions for what fails; True when nothing fails.

        `rounds` is the number of repairs at the most. With 0 the manuscript is assembled, checked and
        typeset once, and what fails is reported and not repaired."""
        for round_number in range(rounds + 1):
            tex, spans, _ = self.assemble()
            remove_pdf(self.out)  # a PDF beside the manuscript is always a PDF of it
            found = machine_findings(self.materials, self.plan, self.parts,
                                     [(row['label'], row['key'], row['proof']) for row in self.instances()])
            kind, problems, where = 'machine', [item['problem'] for item in found], [item['part'] for item in found]
            self.event('check', check=MACHINE, problems=problems)
            if not problems and self.recipe:
                folder = self.out / 'typeset'
                folder.mkdir(exist_ok=True)
                for name in ('paper.tex', 'references.bib'):
                    shutil.copyfile(self.out / name, folder / name)
                # TeX stops at its first error and names the line at which it noticed it, which can lie after the
                # part that caused it. So an error of the typesetting goes to the session that may change every part.
                kind, problems = 'typeset', typeset(folder, self.recipe)
                where = [None] * len(problems)
                self.event('check', check=TYPESETTING, command=self.recipe[0], problems=problems)
                if not problems:
                    shutil.copyfile(folder / 'paper.pdf', self.out / 'paper.pdf')
                    kind, problems = 'wide', wide_lines(folder / 'paper.log') + tight_displays(folder, self.recipe)
                    where = [part_at(spans, int(line[1])) if (line := WIDE_LINE.match(problem)) else None
                             for problem in problems]
                    self.event('check', check=WIDE, problems=problems)
            # What an earlier pass left open about the machine checks, the typesetting or wide lines is replaced by
            # what this pass finds.
            self.open = [item for item in self.open if item['check'] not in (MACHINE, TYPESETTING, WIDE)]
            if not problems:
                self.save()
                return True
            if kind == 'wide':
                # A wide line that lies in no part stands in what the script supplied: a title or a heading of the
                # plan, the author lines, the bibliography. A repair changes the parts and keeps all of these, so
                # such a line goes to no session and is reported with the lines that the repairs leave.
                held = [(problem, part) for problem, part in zip(problems, where) if part is not None]
                if not held:
                    break
                if round_number < rounds:
                    self.repair(kind, [problem for problem, _ in held], [part for _, part in held], tex, spans)
            elif round_number < rounds:
                self.repair(kind, problems, where, tex, spans)
        if kind == 'wide':
            # The paper is typeset. A line that still stands out into the margin is reported and stops nothing.
            self.open.append({'check': WIDE, 'after_repairs': round_number, 'problems': problems})
            self.save()
            return True
        self.open.append({'check': TYPESETTING if kind == 'typeset' else MACHINE, 'after_repairs': rounds,
                          'problems': problems})
        self.save()
        return False

    def repair(self, kind, findings, where, tex=None, spans=None, narrow=False, numbers=None):
        """Sessions that change the parts for what a check or a reader found; returns what the log has of the repair.

        `where` names for each finding the part it concerns, or None. The findings of one section go to a
        session for that section, which has the section's brief and changes that section only, and
        these sessions run side by side; the abstract goes with the introduction. What concerns no
        single section goes to one session that may change every part, after the others, on the
        manuscript as they left it. After a reading that session is always launched: it is the one that
        compares what the reader understood with the research.

        A narrow repair is the last one its findings receive: its sessions are told to change the
        passages their findings name and nothing else, the session for the whole is launched only for
        findings that concern no single section, and what they change does not count as a rewriting of
        the manuscript, because narrow_run has every changed passage read. `numbers` are then the
        numbers under which the log knows the findings; without it they are counted from 1."""
        if tex is None:
            tex, spans, _ = self.assemble()
        sections = self.plan['sections']
        items = findings['findings'] if kind == 'reading' else findings
        home = {'abstract': sections[0]['id'], **{section['id']: section['id'] for section in sections}}
        where = [home.get(part) for part in where]
        groups = [(section, [n for n, sid in enumerate(where) if sid == section['id']]) for section in sections]
        groups = [(section, numbers) for section, numbers in groups if numbers]
        rest = [n for n, sid in enumerate(where) if sid is None]

        def one(section, places, tex, spans):
            return self.repair_session(kind, section, [items[n] for n in places], findings, tex, spans, narrow)

        number = lambda n: numbers[n] if numbers else n + 1
        results = self.side_by_side([lambda section=section, places=places: one(section, places, tex, spans)
                                     for section, places in groups])
        if rest or (kind == 'reading' and not narrow):
            if any(changed for changed, _ in results):
                tex, spans, _ = self.assemble()
            results.append(one(None, rest, tex, spans))
            groups.append((None, rest))
        changed = sorted({name for names, _ in results for name in names})
        response = None
        if kind in NARROW_KINDS.values():
            # The answers of the sessions, in the order and with the numbers of the findings as they were reported.
            answers = {n: {**answer, 'finding': number(n)} for (_, places), (_, answered) in zip(groups, results)
                       for n, answer in zip(places, answered)}
            response = [answers[n] for n in sorted(answers)]
        report = {'changed': changed, 'response': response,
                  'sessions': [{'section': section['id'] if section else None, 'findings': [number(n) for n in places],
                                'changed': names} for (section, places), (names, _) in zip(groups, results)]}
        self.event('repair', of=kind, **({'narrow': True} if narrow else {}), **report)
        return report

    def repair_session(self, kind, section, items, report, tex, spans, narrow=False):
        """One repair session, for one section or, without `section`, for the whole; the parts it changed and its answers."""
        sections = self.plan['sections']
        first = section is sections[0]
        names = list(self.parts) if section is None else [section['id']] + (['abstract'] if first else [])
        answers = kind in NARROW_KINDS.values()  # the kinds whose session answers each finding: revised, or kept and why
        # A finding about the running text has a third answer: its passage was moved into the proof that uses it.
        actions = ('revised', 'moved', 'kept') if kind == 'coverage' else ('revised', 'kept')
        told_response = RESPONSE_MOVED if kind == 'coverage' else RESPONSE

        def read(output):
            changed = {name: text for name, text in written_parts(output, names).items() if text != self.parts[name]}
            response = None
            if answers:
                response = self.load(output / 'response.json', list)
                if not answered_each(response, len(items), actions):
                    raise Unusable([f'output/response.json has one object for each of the {len(items)} findings, with an '
                                    '"action" of ' + ' or '.join(f'"{action}"' for action in actions) + ' and a "note"'])
                faults = [fault for item, r in zip(items, response) if r['action'] == 'moved'
                          for fault in self.move_faults(item, {**self.parts, **changed}, spans)]
                if faults:
                    raise Unusable(faults)
                # A move is a change like every other from here on: it is settled and read with the others.
                response = [{**r, 'action': 'revised', 'moved': True} if r['action'] == 'moved' else r for r in response]
            if not changed and (not answers or any(r['action'] == 'revised' for r in response)):
                raise Unusable(['no part was changed: write the complete new text of each part you change as '
                                'output/<name>.tex, with the file name it has in parts/'])
            return changed, response

        found = {'understanding': report['understanding'], 'findings': items} if kind == 'reading' else items
        given = {'paper.tex': tex, 'findings.json': json.dumps(found, ensure_ascii=False, indent=2) + '\n',
                 **{f'parts/{name}.tex': self.parts[name] for name in names}}
        if kind == 'coverage' and any('source' in item for item in items):
            # A finding about a cited work is answered from what the work says, which the draft carries.
            given['attributions.json'] = json.dumps((self.sketched or {}).get('attributions') or [],
                                                    ensure_ascii=False, indent=2) + '\n'
        lines = '; '.join(f'lines {a} to {b} are `parts/{name}.tex`' for name, a, b in spans if name in names)
        told = ((NARROW_WHOLE_KINDS if section is None else NARROW_SECTION_KINDS)[kind]
                + (NARROW_AGAIN if any('open_because' in item for item in items) else '')) if narrow \
            else (WHOLE_KINDS if section is None else SECTION_KINDS)[kind]
        if section is None:
            papers = {s['id']: self.section_papers(s) for s in sections}
            files = {'paper-method.md': method_before_checks(), 'user-writing-preferences.md': read_file(PREFERENCES),
                     'plan.json': self.plan_text(), **self.records(), **given}
            if self.collection is not None:
                files['study.md'] = self.study
                files.update({f'exemplars/{key}.tex': self.papers[key] for keys in papers.values() for key in keys})
            prompt = REPAIR_PROMPT.format(
                kind=told, response=told_response if answers else '', spans='Its ' + lines + '.',
                papers=REPAIR_PAPERS.format(papers='; '.join(
                    f"section `{sid}`, " + ' and '.join(f'`exemplars/{key}.tex`' for key in keys)
                    for sid, keys in papers.items())) if self.collection is not None else '',
                **self.research_note())
        else:
            papers = self.section_papers(section)
            files = {**self.kit(section), **given}
            prompt = SECTION_REPAIR_PROMPT.format(
                id=section['id'], title=section['title'], kind=told, response=told_response if answers else '',
                also=' As the first section it is the introduction, and this session repairs the abstract with it.' if first else '',
                spans='Its ' + lines + '.', held=' and '.join(f'`parts/{name}.tex`' for name in names),
                what='each part you change' if first else 'the part',
                outputs=' and '.join(f'`output/{name}.tex`' for name in names),
                papers=SECTION_PAPERS_FILES.format(count=len(papers), papers=' and '.join(
                    f'`exemplars/{key}.tex`' for key in papers)) if self.collection is not None else '',
                **self.research_note(section))
        changed, response = self.session('repair', prompt, files, read, self.writer,
                                         ('narrow-' if narrow else '') + (kind if section is None else f"{kind}-{section['id']}"))
        with self.lock:
            if changed and kind in ('likeness', 'comparison') and not narrow:
                # Recorded before the parts are replaced, so that a run stopped just here still reads what was rewritten.
                self.rewritten = True
                self.save()
            self.keep(changed)
        return sorted(changed), response

    def move_faults(self, finding, parts, spans):
        """Why a repair session's move of a passage is not accepted, as sentences for the next session; none when it is.

        `finding` is a finding about the running text whose passage the session says it moved into
        the proof that uses it, and `parts` are the parts as the session left them. A move changes
        where a passage stands and not what it says, so the passage that the finding quotes has to
        stand inside a proof, word for word, and no longer in the text that is compared with the
        elements (running_text). A formula of the passage that carries a label has to stand before
        every reference to it, since a derivation can be moved behind a place that uses it."""
        quote, faults = collapsed(finding['quote']), []
        inside = collapsed(' '.join(proof[0] for text in parts.values() for proof in PROOF_ENVIRONMENT.finditer(text)))
        compared = collapsed(' '.join(entry['text'] for entries in running_text(self.plan, parts, spans).values()
                                      for entry in entries))
        said = shortened(quote, 160)
        if quote not in inside:
            faults.append(f'the passage "{said}" was answered with "moved", and it does not stand inside a proof '
                          'unchanged: move it as it is, or answer with "revised" when you reworded it')
        if quote in compared:
            faults.append(f'the passage "{said}" was answered with "moved", and it still stands outside the proofs, or '
                          'text outside its proof still refers to its formula')
        order = ['abstract'] + [section['id'] for section in self.plan['sections']]
        whole = '\n'.join(uncommented(parts[name]) for name in order)
        for label in LABEL.findall(finding['quote']):
            at = whole.find('\\label{' + label + '}')
            early = [match for match in REF.finditer(whole) if label in [target.strip() for target in match[1].split(',')]
                     and match.start() < at]
            if at >= 0 and early:
                faults.append(f'the formula with \\label{{{label}}} now stands after a place that refers to it; put the '
                              'derivation before its first use')
        return faults

    def read_and_repair(self):
        """Independent readings of the manuscript; a repair of what the reader found follows each of them.

        The repair after every reading but the last may rewrite, and the next reading reads what it
        left. The repair after the last reading is narrow, and a session reads the passages it changed
        (narrow_run). So the manuscript these readings leave consists of text that the last reader read
        and of changes that were found sound, and what stays open is what that repair kept, what was
        undone, or what a sound change did not answer. A reading speaks for the manuscript as it then stands, so it replaces what an earlier
        reading left open. A run that was stopped inside the narrow repair or the reading of its changes
        is continued there, and its readings are not made again."""
        if self.narrowing(READING):
            return self.narrow_finish() and self.read_through()
        reader = method_part(READER_SECTION)

        def read(output):
            report = self.load(output / 'reading.json')
            findings = report.get('findings')
            if not report.get('understanding') or not isinstance(findings, list) \
                    or not all(isinstance(f, dict) and is_text(f.get('where')) and is_text(f.get('problem')) for f in findings):
                raise Unusable(['output/reading.json has "understanding" and "findings", an array whose entries have a '
                                '"where" and a "problem"'])
            return report

        for number in range(1, READING_ROUNDS + 1):
            self.readings += 1  # counted over the whole run, so the log tells the later readings from the first ones
            self.save()
            files = {'paper.tex': read_file(self.out / 'paper.tex'), 'references.bib': self.materials['bibliography']}
            report = self.session('read', READ_PROMPT.format(reader=reader), files, read, self.assessor,
                                  check={None: 'the reading of the manuscript as it then stood by a session that has the '
                                               'manuscript and nothing else'})
            if report is None:
                # The reading was not made (session). The same manuscript would be given to the next one, so the
                # readings end here, and what an earlier reading left open stays as it is.
                break
            self.event('reading', round=self.readings, understanding=report['understanding'], findings=report['findings'])
            self.open = [item for item in self.open if item['check'] != READING]
            if not report['findings']:
                break
            if number == READING_ROUNDS:
                # What the last reading found is open until the narrow repair and the reading of its changes are done.
                self.open.append({'check': READING, 'after_repairs': READING_ROUNDS - 1, 'problems': report['findings']})
                self.narrow_begin(READING, understanding=report['understanding'])
                if not self.narrow_finish():
                    return False
                break
            self.repair('reading', {'understanding': report['understanding'], 'findings': report['findings']},
                        [named_part(self.plan, finding.get('section')) for finding in report['findings']])
            if not self.settle():
                return False
        return self.read_through()

    def read_through(self):
        """Record that the manuscript as it stands has been read by itself.

        This is recorded only at the end of the readings: a run that is stopped before this point makes
        them again. A narrow repair leaves the record as it is: every passage it changed was read
        where it stands and found sound, or put back as the last reader read it."""
        self.rewritten = False
        self.save()
        return True

    def read_again(self):
        """The readings of the manuscript by itself, made again when a repair has rewritten it since.

        A repair that follows a reading beside real papers rewrites passages for their manner, and one
        that follows a comparison corrects a statement and adjusts its proof. Either can change what a
        proof says or take out a step that the reader needs. The machine checks do not see that, and the
        comparison sees only the numbered statements. So whenever such a repair changed a part, a reader
        who has nothing but the manuscript reads what it left, in the same way and within the same bound
        as before. When none did, the manuscript is as its last reading left it and is not read again.
        False only when a repair leaves the manuscript failing."""
        return not self.rewritten or self.read_and_repair()

    def read_beside_papers(self):
        """Readings of the manuscript beside papers the plan did not choose, each with the next ones of their list.

        They go on until LIKENESS_CLEAN readings in succession find no departure, and there are at most
        LIKENESS_ROUNDS. When the papers of the list are used up, the readings take them again from the
        first. A reading with departures is followed by a repair. After the last reading that the bound
        allows, the repair is narrow and a session reads the passages it changed (narrow_run); what it
        kept, what was undone, or what a sound change did not answer stays open. When the last reading found nothing and the one before it
        had departures, those were repaired and one reading has confirmed the repair where two are asked
        for, so they stay open with that reason. The comparison is made in either case, after read_again
        when a repair that may rewrite changed a part. False only when a repair leaves the manuscript
        failing. A run that was stopped inside the narrow repair or the reading of its changes is
        continued there."""
        if self.narrowing(LIKENESS):
            return self.narrow_finish()
        section = method_part(LIKENESS_SECTION)
        order = likeness_papers(self.collection, self.plan['exemplars'])
        # These readings speak for the manuscript as they find it, so they replace what earlier ones left open.
        self.open = [item for item in self.open if item['check'] != LIKENESS]
        clean, repairs, left = 0, 0, None
        for round_number in range(1, LIKENESS_ROUNDS + 1):
            start = (round_number - 1) * LIKENESS_PAPERS
            keys = [order[(start + i) % len(order)] for i in range(LIKENESS_PAPERS)]
            tex = read_file(self.out / 'paper.tex')

            def read(output):
                report = self.load(output / 'likeness.json')
                problems = check_likeness(report)
                if problems:
                    raise Unusable(problems)
                return report

            files = {'paper.tex': tex, 'references.bib': self.materials['bibliography'],
                     **{f'exemplars/{key}.tex': self.papers[key] for key in keys}}
            prompt = LIKENESS_PROMPT.format(section=section,
                                            papers=', '.join(f'`exemplars/{key}.tex`' for key in keys))
            report = self.session('likeness', prompt, files, read, self.assessor,
                                  check={None: 'the last reading of the manuscript beside published papers'})
            if report is None:
                continue  # not made (session): it counts as one of the readings and confirms nothing
            departures = report['departures']
            self.event('likeness', round=round_number, exemplars=keys, likeness=report['likeness'], departures=departures)
            if not departures:
                clean += 1
                if clean == LIKENESS_CLEAN:
                    return True
                continue
            clean, left = 0, departures
            if round_number == LIKENESS_ROUNDS:
                # What the last reading found is open until the narrow repair and the reading of its changes are done.
                self.open.append({'check': LIKENESS, 'after_repairs': repairs, 'problems': departures})
                self.narrow_begin(LIKENESS)
                return self.narrow_finish()
            # A repair that changed a part has recorded that the manuscript is to be read by itself again; one
            # that kept every passage leaves nothing to read again.
            self.repair('likeness', departures, [named_part(self.plan, departure.get('section')) for departure in departures])
            repairs += 1
            if not self.settle():
                return False
        if left:
            # Reached with one clean reading after the last repair, or with none where a reading was not made.
            reason = ONCE_CONFIRMED if clean else NOT_CONFIRMED
            self.open.append({'check': LIKENESS, 'after_repairs': repairs,
                              'problems': [{**departure, 'open_because': reason} for departure in left]})
        self.save()
        return True

    def compare(self):
        """Every numbered statement against the statement of its element; a repair follows all but the last comparison.

        The statements are compared section by section, the sections side by side: each session has the
        statements of one section and the records of their elements. A difference that the last
        comparison finds is open, and the stages after this one are made all the same: they do not
        depend on that statement, and the pass that later acts on it does not make them. False only
        when a repair leaves the manuscript failing."""
        # In a run that was not stopped, the manuscript has just been read. In one that is continued inside this
        # stage, a repair of what an earlier comparison found may have rewritten it since; it is read first.
        if not self.read_again():
            return False
        sections = self.plan['sections']
        home = {item['label']: item['section'] for item in self.plan['statements']}
        for round_number in range(1, COMPARISON_ROUNDS + 1):
            tex, spans, rows = self.assemble()
            groups = [(section, [row for row in rows if home[row['label']] == section['id']]) for section in sections]
            results = self.side_by_side([lambda section=section, stated=stated: self.compare_section(section, stated, tex, spans)
                                         for section, stated in groups if stated])
            # A section whose comparison was not made (session) has no verdicts of this round. A statement of it keeps
            # the verdict that an earlier round gave its present text, and without such a verdict it stays not compared.
            verdicts = [verdict for result in results if result for verdict in result]
            self.compared = {**{row['label']: self.compared[row['label']] for row in rows
                                if row['comparison']['verdict'] != 'not compared'},
                             **self.kept_verdicts(verdicts, rows)}
            self.save()
            differing = [{'label': row['label'], 'difference': self.compared[row['label']]['difference']} for row in rows
                         if row['label'] in self.compared and self.compared[row['label']]['verdict'] == 'differs']
            # A disagreement inside an element's record is reported beside the paper; no repair of the manuscript removes it.
            disagreements = [{'label': label, 'record_disagreement': judged['record_disagreement']}
                             for label, judged in self.compared.items() if judged['record_disagreement']]
            self.event('comparison', round=round_number, differing=differing, record_disagreements=disagreements)
            self.assemble()
            if not differing:
                return True
            if round_number == COMPARISON_ROUNDS:
                self.open = [item for item in self.open if item['check'] != COMPARISON]
                self.open.append({'check': COMPARISON, 'after_repairs': COMPARISON_ROUNDS - 1, 'problems': differing})
                self.save()
                return True
            # A repair that changed a part corrected statements and adjusted proofs, so the manuscript is read by
            # itself again before its statements are compared once more; the last thing done is then a comparison.
            self.repair('comparison', differing, [home[item['label']] for item in differing])
            if not self.settle() or not self.read_again():
                return False

    @staticmethod
    def kept_verdicts(verdicts, rows):
        """The verdicts of a comparison as `compared` keeps them, by label, each with the digest of the text of its row."""
        digests = {row['label']: row['paper_statement_sha256'] for row in rows}
        return {v['label']: {'verdict': v['verdict'], 'difference': v.get('difference') or '',
                             'record_disagreement': v['record_disagreement'] if is_text(v.get('record_disagreement')) else '',
                             'sha256': digests[v['label']]} for v in verdicts}

    def compare_rows(self, rows, tex, spans):
        """Compare once the numbered statements of these rows of the correspondence, whose present text has no verdict.

        The sections are compared side by side, each by a session that is told that it has only the
        statements that were not compared. The verdicts are kept with those of the other statements,
        and returned."""
        home = {item['label']: item['section'] for item in self.plan['statements']}
        groups = [(section, [row for row in rows if home[row['label']] == section['id']]) for section in self.plan['sections']]
        listed = ('those numbered statements of this section whose present text has not been compared with '
                  'their elements, because a repair changed it or because the comparison did not reach it')
        results = self.side_by_side([lambda section=section, stated=stated:
                                     self.compare_section(section, stated, tex, spans, listed)
                                     for section, stated in groups if stated])
        verdicts = [verdict for result in results if result for verdict in result]
        self.compared.update(self.kept_verdicts(verdicts, rows))
        self.save()
        self.event('comparison', round=1 + sum(event['event'] == 'comparison' for event in self.log),
                   statements=[row['label'] for row in rows],
                   differing=[{'label': v['label'], 'difference': v['difference']}
                              for v in verdicts if v['verdict'] == 'differs'],
                   record_disagreements=[{'label': v['label'], 'record_disagreement': v['record_disagreement']}
                                         for v in verdicts if is_text(v.get('record_disagreement'))])
        return verdicts

    def compare_section(self, section, rows, tex, spans, listed='the numbered statements of this section'):
        """One session that compares the numbered statements of one section; its verdicts, in their order.

        None when the comparison was not made (session); each of these statements is then recorded as
        not compared for that reason."""
        labels = [row['label'] for row in rows]

        def read(output):
            verdicts = self.load(output / 'comparison.json', list)
            if not judged_in_order(verdicts, labels):
                raise Unusable(['output/comparison.json has one object for each entry of statements.json, in their order, '
                                'with its "label", a "verdict" of "same" or "differs", and for "differs" the "difference"'])
            return verdicts

        entries = [{key: row[key] for key in ('label', 'number', 'element', 'record_statement', 'lean_statement',
                                              'paper_statement')} for row in rows]
        files = {'paper-method.md': method_before_checks(),
                 'paper.tex': tex,
                 'statements.json': json.dumps(entries, ensure_ascii=False, indent=2) + '\n',
                 'records.md': render_records(self.materials, self.plan, {row['element'] for row in rows}, self.layout),
                 **{name: text for name, text in self.records().items() if name.startswith('elements')}}
        lines = next(f'Its lines {a} to {b} are this section.' for name, a, b in spans if name == section['id'])
        return self.session('compare', COMPARE_PROMPT.format(title=section['title'], spans=lines, listed=listed), files,
                            read, self.assessor, section['id'],
                            check={row['label']: f"the comparison of {row['number']} (\\label{{{row['label']}}}) with "
                                                 f"the element `{row['element']}` that it states" for row in rows})

    # -- what the readings left open ----------------------------------------------------------------------

    def resolve(self):
        """The stage `resolve`: one session closes the findings that the readings left open; False as the other stages.

        The session may change wording and structure, so it can return a plan with other sections and
        other numbered statements. What it returns is accepted when the plan passes the check of the
        plan and every section of the plan has a part. The steps, each recorded in the state when it is
        complete, so that a run that is stopped is continued at the step it was in:

          session  the session is launched, and what it returned is kept in <out>/resolve: the plan and
                   every part of the manuscript as it now is. In the same record of the state the
                   verdicts of the comparison are reduced to those whose label still states the same
                   element, and a difference of a statement that has no number any more is dropped. A
                   verdict holds for the text it was given for, so a statement that was only moved
                   keeps its verdict and one that was reworded is compared in the stage `coverage`.
          place    the parts and the plan of <out>/resolve take the place of those in <out>: the parts
                   of sections that are gone are removed, and the layout is made from the new plan. The
                   correspondence file follows by itself, since it is made from the plan and the parts.
          settle   the manuscript is assembled, checked by machine and typeset, with the repairs that
                   this needs, as after any repair. The findings of the readings are then closed: one
                   that the session answered with a reason goes to the list `kept`.
          read     when a part changed, the manuscript is read by itself again (read_again), which
                   ends in a narrow repair. What that repair leaves is answered with the reason it
                   gives, and goes to `kept` as well.

        The stage `coverage` follows. False only when the manuscript is left failing its machine checks
        or its typesetting; the findings of the readings then stay open with that."""
        state = self.resolving
        if state is None:
            taken = [(item['check'], problem) for item in self.open if item['check'] in READINGS
                     for problem in item['problems']]
            if not taken:
                return True
            findings = [{'finding': number, 'check': check, 'reported': problem}
                        for number, (check, problem) in enumerate(taken, 1)]
            plan, parts, response = self.resolve_session(findings)
            folder = self.out / 'resolve'
            shutil.rmtree(folder, ignore_errors=True)
            (folder / 'parts').mkdir(parents=True)
            write_json(folder / 'plan.json', plan)
            for name, text in parts.items():
                write_text(folder / 'parts' / (name + '.tex'), text)
            old, new = ({item['label']: item['element'] for item in each['statements']} for each in (self.plan, plan))
            state = {'step': 'place', 'findings': findings, 'response': response, 'plan': plan != self.plan,
                     'changed': sorted(name for name in parts if self.parts.get(name) != parts[name]),
                     'removed': sorted(name for name in self.parts if name not in parts)}
            with self.lock:
                self.compared = {label: judged for label, judged in self.compared.items() if new.get(label) == old.get(label)}
                for item in self.open:
                    if item['check'] == COMPARISON:
                        item['problems'] = [problem for problem in item['problems'] if problem['label'] in new]
                self.open = [item for item in self.open if item['problems']]
                # Recorded before the parts are replaced, so that a run stopped just here still reads what was rewritten.
                self.rewritten = self.rewritten or bool(state['changed'] or state['removed'])
                self.resolving = state
                self.save()
        if state['step'] == 'place':
            plan, names = self.place_resolution()
            self.take_plan(plan, self.study)
            self.parts = {name: read_file(self.out / 'parts' / (name + '.tex')) for name in names}
            self.event('resolve', changed=state['changed'], removed=state['removed'], plan=state['plan'],
                       response=state['response'])
            state['step'] = 'settle'
            self.save()
        if state['step'] == 'settle':
            # A session that kept every passage left the manuscript as it was settled before.
            if (state['changed'] or state['removed'] or state['plan']) and not self.settle():
                return False
            answers = {answer['finding']: answer for answer in state['response']}
            self.kept += [{'check': entry['check'], 'finding': entry['reported'], 'reason': answers[entry['finding']]['note']}
                          for entry in state['findings'] if answers[entry['finding']]['action'] == 'kept']
            self.open = [item for item in self.open if item['check'] not in READINGS]
            state['step'] = 'read'
            self.save()
        if state['step'] == 'read':
            if not self.read_again():
                return False
            self.kept += [{'check': item['check'], 'reason': problem.get('open_because', ''),
                           'finding': {key: value for key, value in problem.items() if key != 'open_because'}}
                          for item in self.open if item['check'] in READINGS for problem in item['problems']]
            self.open = [item for item in self.open if item['check'] not in READINGS]
            self.resolving = None
            self.save()
            shutil.rmtree(self.out / 'resolve', ignore_errors=True)
        return True

    def place_resolution(self):
        """Put the parts and the plan that <out>/resolve holds in the place of those in <out>; the plan and its part names.

        Every part of the new manuscript is written, the parts of sections that the plan no longer has
        are removed, and the plan is written last. Doing it again changes nothing, so a run that was
        stopped while it did this does it again (take_up)."""
        folder = self.out / 'resolve'
        plan = read_json(folder / 'plan.json')
        names = ['abstract'] + [section['id'] for section in plan['sections']]
        (self.out / 'parts').mkdir(exist_ok=True)
        for name in names:
            write_text(self.out / 'parts' / (name + '.tex'), read_file(folder / 'parts' / (name + '.tex')))
        for path in sorted((self.out / 'parts').glob('*.tex')):
            if path.stem not in names:
                path.unlink()
        write_json(self.out / 'plan.json', plan)
        return plan, names

    def resolve_session(self, findings):
        """The session that resolves the open findings of the readings: the plan, every part as it now is, its answers."""
        sections = self.plan['sections']
        tex, spans, _ = self.assemble()
        understanding = next((event['understanding'] for event in reversed(self.log) if event['event'] == 'reading'), None)

        def read(output):
            response = self.load(output / 'response.json', list)
            if not answered_each(response, len(findings)):
                raise Unusable([f'output/response.json has one object for each of the {len(findings)} findings, in their '
                                'order, with an "action" of "revised" or "kept" and a "note"'])
            plan, problems = self.plan, []
            if (output / 'plan.json').is_file():
                plan = self.load(output / 'plan.json')
                problems = check_plan(self.materials, plan, self.keys())
                if not problems and plan.get('exemplars') != self.plan['exemplars']:
                    problems = ['"exemplars" stays as plan.json has it: the papers were chosen and read when the paper '
                                'was planned, and study.md is the account of those papers']
                if problems:
                    raise Unusable(['output/plan.json: ' + problem for problem in problems])
            parts = {}
            for name in ['abstract'] + [section['id'] for section in plan['sections']]:
                path = output / (name + '.tex')
                if path.is_file() and read_file(path).strip():
                    parts[name] = read_file(path)
                elif name in self.parts:
                    parts[name] = self.parts[name]
                else:
                    problems.append(f'output/plan.json has the section `{name}`, and its part output/{name}.tex was not '
                                    'written')
            if problems:
                raise Unusable(problems)
            if plan == self.plan and parts == self.parts and any(r['action'] == 'revised' for r in response):
                raise Unusable(['no part and no plan was changed, and output/response.json says that findings were '
                                'revised: write the complete new text of each part you change as output/<name>.tex, with '
                                'the file name it has in parts/'])
            return plan, parts, [{'finding': number, 'action': r['action'], 'note': r['note'].strip()}
                                 for number, r in enumerate(response, 1)]

        papers = {section['id']: self.section_papers(section) for section in sections}
        files = {'paper-method.md': method_before_checks(), 'user-writing-preferences.md': read_file(PREFERENCES),
                 'plan.json': self.plan_text(), **self.records(), 'paper.tex': tex,
                 'findings.json': json.dumps({'understanding': understanding, 'findings': findings},
                                             ensure_ascii=False, indent=2) + '\n',
                 **{f'parts/{name}.tex': text for name, text in self.parts.items()}}
        if self.collection is not None:
            files['study.md'] = self.study
            files.update({f'exemplars/{key}.tex': self.papers[key] for keys in papers.values() for key in keys})
        prompt = RESOLVE_PROMPT.format(
            spans='Its ' + '; '.join(f'lines {a} to {b} are `parts/{name}.tex`' for name, a, b in spans) + '.',
            papers=REPAIR_PAPERS.format(papers='; '.join(
                f"section `{sid}`, " + ' and '.join(f'`exemplars/{key}.tex`' for key in keys)
                for sid, keys in papers.items())) if self.collection is not None else '',
            plan_keys=PLAN_KEYS + PLAN_ACCEPTS + main_note(self.materials), **self.research_note())
        return self.session('resolve', prompt, files, read, self.writer)

    # -- the running text -----------------------------------------------------------------------------------

    def cover(self):
        """The stage `coverage`: the running text of every section against the elements; False as narrow_run.

        First the numbered statements whose present text has no verdict are compared, once: a repair
        after the comparison of the statements, or the session of the stage `resolve`, may have changed
        them. One that differs then is open, and is not repaired here. Then, for each section, a
        session reports the sentences of the running text, and the formulas of a proof that are
        referred to from outside it, that assert mathematics which no element states. When the paper
        is written from a draft that carries the words of the cited works, the session also reports
        each sentence about a cited work that none of those words supports (cover_section). What is
        reported goes to one narrow repair, which cuts a passage, rewords it, or moves a derivation
        into the proof that uses it (repair_session, move_faults), and whose changes are read
        (narrow_run). The sections that the repair changed are covered once more, and what is
        reported then, with what the repair kept in the other sections, is open. No further round
        follows. A run that was stopped inside the repair, the reading of its changes or the second
        covering is continued there."""
        if not self.narrowing(COVERAGE):
            tex, spans, rows = self.assemble()
            rows = [row for row in rows if row['comparison']['verdict'] == 'not compared']
            if rows:
                verdicts = self.compare_rows(rows, tex, spans)
                item = next((item for item in self.open if item['check'] == COMPARISON), None)
                judged = {verdict['label'] for verdict in verdicts}
                problems = [problem for problem in (item['problems'] if item else []) if problem['label'] not in judged] \
                    + [{'label': verdict['label'], 'difference': verdict['difference'], 'open_because': DIFFERS_LATE}
                       for verdict in verdicts if verdict['verdict'] == 'differs']
                self.open = [other for other in self.open if other['check'] != COMPARISON]
                if problems:
                    self.open.append({'check': COMPARISON, 'after_repairs': item['after_repairs'] if item else 0,
                                      'problems': problems})
                # Saved here, before the sessions that compare the running text: a run that one of them stops is
                # continued with these verdicts already kept (compare_rows), so nothing would find the difference again.
                self.save()
                tex, spans, _ = self.assemble()  # the correspondence file with these verdicts
            found = self.cover_sections([section['id'] for section in self.plan['sections']], tex, spans)
            self.open = [item for item in self.open if item['check'] != COVERAGE]
            problems = [finding for findings in found.values() for finding in findings]
            if not problems:
                self.save()
                return True
            # What was found is open until the narrow repair, the reading of its changes and the second covering are done.
            self.open.append({'check': COVERAGE, 'after_repairs': 0, 'problems': problems})
            self.narrow_begin(COVERAGE)
        passed = self.narrow_run()
        self.narrow_end(self.cover_again() if passed else None)
        return passed

    def cover_sections(self, ids, tex, spans):
        """Sessions that compare the running text of the sections `ids` with the elements, side by side.

        Returns for each of these sections what its session reported, in the order of the paper; a
        section without running text has no session and nothing reported."""
        entries = running_text(self.plan, self.parts, spans)
        sections = [section for section in self.plan['sections'] if section['id'] in ids]
        covered = [section for section in sections if entries[section['id']]]
        results = self.side_by_side([lambda section=section: self.cover_section(section, entries[section['id']], tex, spans)
                                     for section in covered])
        found = {section['id']: [] for section in sections}
        found.update({section['id']: result for section, result in zip(covered, results)})
        self.event('coverage', round=1 + sum(event['event'] == 'coverage' for event in self.log),
                   sections=[section['id'] for section in covered],
                   uncovered=[finding for findings in found.values() for finding in findings])
        return found

    def cover_section(self, section, entries, tex, spans):
        """One session that compares the running text of one section with the elements; what it reports, as findings."""
        elements, numbers = self.layout.elements, {entry['entry']: entry for entry in entries}
        first = section is self.plan['sections'][0]
        # What the cited works say at the places where the records cite them, when the draft carries it: the
        # sentences of the running text about the literature are then held to these quotations.
        store = (self.sketched or {}).get('attributions') or []
        keys = set(self.materials['bibliography_keys'])

        def read(output):
            found = self.load(output / 'coverage.json', list)
            # A finding names the element that comes nearest, or, for a sentence about a cited work, the work.
            named = lambda item: (store and isinstance(item['source'], str) and item['source'] in keys) \
                if 'source' in item else item.get('nearest') in elements
            if not all(isinstance(item, dict) and not isinstance(item.get('entry'), bool) and item.get('entry') in numbers
                       and is_text(item.get('quote')) and is_text(item.get('difference')) and named(item) for item in found):
                raise Unusable(['output/coverage.json is an array, empty when an element covers every assertion; each '
                                'object has "entry", the number of an entry of text.json, "quote" and "difference" as '
                                'texts that are not empty, and "nearest", the name of an element as elements.md gives it'
                                + (', or in its place "source", a key of references.bib, for a sentence about a cited '
                                   'work' if store else '')])
            loose = [item['entry'] for item in found
                     if collapsed(item['quote']) not in collapsed(numbers[item['entry']]['text'])]
            if loose:
                raise Unusable(['output/coverage.json: "quote" is copied exactly from the text of its entry, without a word '
                                'left out or changed, because the passage is later found in the manuscript by it; it is '
                                'not in the entries ' + ', '.join(str(entry) for entry in loose)])
            return found

        files = {'paper-method.md': method_before_checks(),
                 'paper.tex': tex,
                 'text.json': json.dumps(entries, ensure_ascii=False, indent=2) + '\n',
                 'records.md': render_section_records(self.materials, self.plan, section, self.layout),
                 **{name: text for name, text in self.records().items() if name.startswith('elements')},
                 **({'attributions.json': json.dumps(store, ensure_ascii=False, indent=2) + '\n',
                     'references.bib': self.materials['bibliography']} if store else {})}
        lines = ' '.join(f"Its lines {a} to {b} are {'the abstract' if name == 'abstract' else 'this section'}."
                         for name, a, b in spans if name == section['id'] or (first and name == 'abstract'))
        prompt = COVER_PROMPT.format(
            title=section['title'], spans=lines,
            abstract=', or "abstract" for the abstract, which is compared with this section' if first else '',
            main=COVER_ABSTRACT.format(name=self.materials['main']) if first else '',
            attributions=('- `attributions.json` holds what the cited works say at the places where the records cite '
                          'them, and `references.bib` is the bibliography; the text below says how they are used.\n')
            if store else '',
            literature=COVER_ATTRIBUTIONS if store else COVER_LITERATURE,
            sourced=' and a quotation supports every sentence about a cited work' if store else '',
            source=COVER_SOURCE if store else '')
        title = collapsed(section['title'])
        found = self.session('cover', prompt, files, read, self.assessor, section['id'],
                             check={None: f'the comparison of the running text of the section "{title}" with the elements'})
        if found is None:
            return []  # not made (session): nothing is reported for this section, and the record says so

        def where(entry):
            if entry['part'] == 'abstract':
                return 'the abstract'
            return (f'the running text of the section "{title}"' if entry['kind'] == 'running text'
                    else f"the formula {', '.join(entry['labels'])} in a proof of the section \"{title}\"")

        return [{'where': where(numbers[item['entry']]),
                 'section': 'abstract' if numbers[item['entry']]['part'] == 'abstract' else 'sec:' + section['id'],
                 'quote': item['quote'].strip(), 'asserts': item['asserts'].strip() if is_text(item.get('asserts')) else '',
                 'nearest': '' if 'source' in item else item['nearest'],
                 **({'source': item['source']} if 'source' in item else {}),
                 'difference': item['difference'].strip()} for item in found]

    def cover_again(self):
        """The running text of the sections that a narrow repair changed, compared with the elements once more.

        The sections are those of which a part differs from the text before the repair, which
        <out>/narrow/before holds; the abstract counts with the first section. Returns for each of
        them what is reported now, an empty list where nothing is; narrow_end puts that in the place
        of what was open in those sections."""
        sections = self.plan['sections']
        before = {name: read_file(self.out / 'narrow' / 'before' / (name + '.tex')) for name in self.parts}
        home = {'abstract': sections[0]['id'], **{section['id']: section['id'] for section in sections}}
        changed = {home[name] for name in self.parts if self.parts[name] != before[name]}
        if not changed:
            return {}
        tex, spans, _ = self.assemble()
        return self.cover_sections(changed, tex, spans)

    def cover_repaired(self):
        """The running text of the sections that a repair has changed since a closing pass began, compared once more.

        A closing pass settles the manuscript after it has restated statements or taken passages out
        (close), and a run that is continued after such a pass was stopped settles it again
        (after_writing). The settling can launch a repair of the LaTeX, and what that session writes
        outside the numbered statements has been compared with nothing. So each section of which
        such a repair changed a part is compared with the elements once more (cover_sections), the
        abstract with the first section. What is reported is entered in `closed` and stays in the
        paper: no repair follows, as none follows for a numbered statement that such a repair changed.
        The log says which sections are due: those of the parts that a `repair` event names after
        the first `closing` event, unless a later `coverage` event names the section. A run that had
        no closing pass launches nothing here."""
        begun = next((number for number, event in enumerate(self.log) if event['event'] == 'closing'), len(self.log))
        sections = self.plan['sections']
        home = {'abstract': sections[0]['id'], **{section['id']: section['id'] for section in sections}}
        due = set()
        for event in self.log[begun:]:
            if event['event'] == 'repair':
                due |= {home[name] for name in event['changed'] if name in home}
            elif event['event'] == 'coverage':
                due -= set(event['sections'])
        if not due:
            return
        tex, spans, _ = self.assemble()
        found = self.cover_sections(due, tex, spans)
        with self.lock:
            # What an earlier comparison of this kind recorded for these sections gives way to what is reported now.
            self.closed = [entry for entry in self.closed if entry['kind'] != 'uncovered'
                           or home.get(named_part(self.plan, entry.get('section'))) not in due] \
                + [{'kind': 'uncovered', **finding} for findings in found.values() for finding in findings]
            self.save()

    def instances(self):
        """The numbered statements that the paper proves from a cited general theorem, as the draft found them.

        The draft that the paper is written from lists, under "instances", the elements that are an
        instance of a theorem of the literature, each with the work, the place in it, the theorem and
        the specialisation (instance_lines). Returned are those whose element the plan numbers and
        proves, each with its label, the section that writes its proof, and what the draft says of it.
        A paper that is not written from a draft has none."""
        found = []
        for entry in (self.sketched or {}).get('instances') or []:
            item = self.layout.numbered.get(entry.get('element'))
            proof = self.layout.proof_of(item) if item else None
            if proof in self.layout.ids and entry.get('key') in self.materials['bibliography_keys']:
                found.append({'label': item['label'], 'proof': proof, **{key: entry[key] for key in
                                                                        ('element', 'key', 'where', 'states', 'specialisation')}})
        return found

    def text_digest(self):
        """What a check of the places speaks for: the parts as they stand, and what the plan does with the other elements."""
        return sha256_text(json.dumps([sorted(self.parts.items()), self.plan['others']], sort_keys=True))

    def place(self):
        """The stage `placement`: where the manuscript has the elements that the paper gives no number; always True.

        The correspondence file says of every element without a number what the plan did with it: into
        which proofs or into which section it was absorbed, or which section cites it. The writers
        wrote the sections from that plan. A repair can reword such a sentence, move it into a proof
        or cut it. So when a part is no longer as its writer left it, one session reads the
        manuscript as it stands and says of each of these elements whether the manuscript has its
        content, and where. What it says stands in the correspondence file under "in_text" of the
        element, and no repair follows it. The check is made once for a text: at the end of the
        stages, and again after a pass that changed a part (act, close). A manuscript that no repair
        changed needs none, and its elements carry no "in_text". When the check was not made
        (session), they carry none either, and the file lists the check under "not_done"."""
        entries = [item for item in self.plan['others'] if item['treatment'] in ('absorbed', 'cited')]
        digest = self.text_digest()
        if not entries or (self.placed or {}).get('digest') == digest:
            return True
        tex, spans, _ = self.assemble()
        elements = self.layout.elements
        labels = {item['element']: item['label'] for item in self.plan['statements']}
        listed = [{'element': item['element'],
                   'statement': elements[item['element']]['statement'] or elements[item['element']]['lean'],
                   'treatment': item['treatment'],
                   'planned': [labels.get(target) or 'sec:' + target for target in item['into']]
                   if item['treatment'] == 'absorbed' else ['sec:' + item['section']]} for item in entries]
        names = [entry['element'] for entry in listed]

        def read(output):
            found = self.load(output / 'placement.json', list)
            if [entry.get('element') if isinstance(entry, dict) else None for entry in found] != names \
                    or not all(isinstance(entry.get('found'), bool) and isinstance(entry.get('where', ''), str)
                               and isinstance(entry.get('note', ''), str)
                               and (not entry['found'] or entry.get('where', '').strip()) for entry in found):
                raise Unusable(['output/placement.json has one object for each entry of placed.json, in their order, with '
                                'its "element", "found" as true or false, "where" as a text that is not empty when the '
                                'element is found, and "note" as a text'])
            return {entry['element']: {'found': entry['found'],
                                       'where': entry.get('where', '').strip() if entry['found'] else '',
                                       'note': entry.get('note', '').strip()} for entry in found}

        files = {'paper.tex': tex, 'placed.json': json.dumps(listed, ensure_ascii=False, indent=2) + '\n',
                 **{name: text for name, text in self.records().items() if name.startswith('elements')}}
        lines = ' '.join(f"Its lines {a} to {b} are {'the abstract' if name == 'abstract' else 'the section sec:' + name}."
                         for name, a, b in spans)
        found = self.session('place', PLACE_PROMPT.format(spans=lines), files, read, self.assessor,
                             check={None: 'the check of where the manuscript has the content of the elements that have '
                                          'no numbered statement'})
        self.placed = {'digest': digest, 'found': found}
        self.save()
        if found is not None:
            self.event('placement', missing=[name for name in names if not found[name]['found']])
        self.assemble()
        return True

    def after_writing(self):
        """The checks, the readings and the comparison of the manuscript, each stage once.

        The manuscript is settled first, in a run that is continued as in a new one, so that paper.tex is
        the parts as they stand. state.json then says which stages are complete; a stage that was begun
        and not ended is made again from its start, which every stage allows, since each works on the
        parts as they stand and is bounded."""
        # The parts as their writers left them are the text for which the plan says where each element without a
        # number stands. A check of that (place) is due once a repair has changed a part.
        if self.placed is None and not self.done:
            self.placed = {'digest': self.text_digest(), 'found': None}
            self.save()
        # A narrow repair that is under way settles the manuscript itself, from the text that was read.
        if False in self.done.values() or (self.narrow is None and not self.settle()):
            return
        for name, method in STAGES:
            if name not in self.done:
                self.done[name] = bool(getattr(self, method)())
                self.save()
            if not self.done[name]:
                return
        # A pass over what a finished run left open ends with the check of the places (act, close), and a closing
        # pass before that with the comparison of the sections that a repair of the LaTeX changed (cover_repaired).
        # A run that is continued after such a pass was stopped there comes here with every stage complete, and
        # both are made now, for the text as the pass left it. For a text that was checked, and in a run that had
        # no closing pass, they launch nothing.
        self.cover_repaired()
        self.place()

    def finish(self):
        _, _, rows = self.assemble()
        # A verdict of the comparison holds for the text that was compared. A statement without one for its present
        # text stays open, because nothing after this point compares it: the comparison did not reach it, or a repair
        # changed it afterwards, as a repair of the typesetting under --typeset-only can.
        # A statement whose comparison was not made (session) is not open either: the comparison was tried within its
        # attempts, and the run records it as not done.
        uncompared = [{'label': row['label'], 'number': row['number']}
                      for row in rows if row['comparison']['verdict'] == 'not compared' and 'not_done' not in row['comparison']]
        self.open = [item for item in self.open if item['check'] != UNCOMPARED]
        if uncompared:
            self.open.append({'check': UNCOMPARED, 'after_repairs': 0, 'problems': uncompared})
        self.save()
        status = 'open_findings' if self.open else 'complete' if self.recipe else 'no_tex'
        self.event('end', status=status, open=list(self.open), kept=list(self.kept),
                   **({'closed': list(self.closed)} if self.closed else {}),
                   **({'not_done': list(self.undone)} if self.undone else {}))
        print(f'The manuscript is {self.out / "paper.tex"}; the log is {self.out / "log.json"}.')
        for line in not_done_lines(self.undone):
            print(line)
        if self.closed:
            count = lambda kind: sum(entry['kind'] == kind for entry in self.closed)
            differing = sum(entry['kind'] == 'differs' or (entry['kind'] == 'restated' and entry['verdict'] != 'same')
                            for entry in self.closed)
            print(f"What the bounded repairs had left open was closed without a person: {count('removed')} passages that "
                  f"no element covers were taken out, and {count('restated')} statements were restated as their elements "
                  'say them; the last `end` event of log.json lists them under "closed".'
                  + (f' The comparison that followed did not find {differing} statements to say what their elements '
                     'say; the same list has each with its verdict.' if differing else '')
                  + (f" In the sections that a repair of the LaTeX changed during that pass, {count('uncovered')} "
                     'passages of the running text were then found that no element covers; they stay in the paper, '
                     'and the same list has each.' if count('uncovered') else ''))
        if self.kept:
            print(f'{len(self.kept)} findings of the readings were answered with a reason, and the text stays as it is '
                  'there; the last `end` event of log.json lists them under "kept", each with the reason.')
        if self.open:
            print('Findings are left open after the bounded repairs:')
            for item in self.open:
                print(f"- {item['check']}: {len(item['problems'])} left; log.json has them")
            if not any(item['check'] in (MACHINE, TYPESETTING) for item in self.open):
                print('This command with the same --out and --open-findings --dry-run lists them with their numbers; '
                      'with --open-findings, or --open-findings and some of those numbers, it acts on them.')
        if not self.recipe:
            print('No TeX command was available (none of ' + ', '.join(ENGINES) + ' is on PATH, and --tex was not given), '
                  'so paper.pdf was not typeset. Everything else is done. When a TeX command is available, run this '
                  'command again with --typeset-only and the same --out.')
        elif (self.out / 'paper.pdf').is_file():
            print(f'The paper is {self.out / "paper.pdf"}.')
        return {'complete': 0, 'open_findings': 2, 'no_tex': 3}[status]

    # -- the last repair of findings, and the reading of what it changed ------------------------------------

    def narrowing(self, check):
        """Whether a narrow repair of findings of this check is under way, as in a run that was stopped inside one."""
        return self.narrow is not None and not self.narrow.get('pass') \
            and any(entry['check'] == check for entry in self.narrow['findings'])

    def narrow_begin(self, check=None, chosen=None, understanding=None, **more):
        """Begin the last repair of findings that the open list holds: keep the parts as they were read, and record it.

        `chosen` gives the findings as (number, check, position among the problems of the open item of that
        check); with `check` they are all the findings of that item, numbered from 1. The parts as they
        stand are those the reading read. They are kept in <out>/narrow/before, because the reading of the
        changes compares with them and puts back from them, and the state records the repair only when they
        are there."""
        if chosen is None:
            item = next(item for item in self.open if item['check'] == check)
            chosen = [(position + 1, check, position) for position in range(len(item['problems']))]
        problems = {item['check']: item['problems'] for item in self.open}
        folder = self.out / 'narrow'
        shutil.rmtree(folder, ignore_errors=True)
        (folder / 'before').mkdir(parents=True, exist_ok=True)
        for name, text in self.parts.items():
            write_text(folder / 'before' / (name + '.tex'), text)
        self.narrow = {'step': 'repair', 'understanding': understanding, **more,
                       'findings': [{'number': number, 'check': check, 'position': position,
                                     'finding': problems[check][position]} for number, check, position in chosen]}
        self.save()

    def narrow_finish(self):
        """The narrow repair that is under way, to its end, with the open list as it leaves it; False as narrow_run."""
        passed = self.narrow_run()
        self.narrow_end()
        return passed

    def narrow_run(self):
        """The last repair of findings, and the reading of what it changed; False only when the manuscript is left failing.

        What has to hold at the end: every passage of the manuscript is text that the reading which
        reported the findings read, or a change that the reading of the changed passages found sound.
        The steps, each recorded in the state when it is complete, so that a run that is stopped is
        continued at the step it was in:

          repair   repair sessions change the passages that the findings name. A repair that was stopped
                   is made again from the parts as they were read.
          settle   the manuscript is assembled, checked by machine and typeset, with the repairs of the
                   LaTeX that this needs. When it still fails after them, every change is undone.
          read     one session has the manuscript and every passage that now differs from the text that
                   was read, with its text before and after, the changes of the settling among them. It
                   says for each whether the change is sound and for which findings it was made, and
                   for each finding whether the changes answer it.
          undo     a change that was found unsound is put back as it was, and with it every other change
                   made for the same findings. The manuscript is then checked and typeset once more,
                   without repairs; when it fails, every change is undone.

        `left` then holds, for every finding that stays open, why: the repair session kept the text,
        or its change was undone, or its change was found not to answer it. A change that is sound and
        does not answer its finding stays, since the text is sound with it. No further round follows."""
        narrow = self.narrow
        before = {name: read_file(self.out / 'narrow' / 'before' / (name + '.tex')) for name in self.parts}
        changed = lambda: [name for name in self.parts if self.parts[name] != before[name]]
        if narrow['step'] == 'repair':
            self.keep({name: before[name] for name in changed()})
            sessions, response = [], []
            home = {item['label']: item['section'] for item in self.plan['statements']}
            for check, kind in NARROW_KINDS.items():
                taken = [entry for entry in narrow['findings'] if entry['check'] == check]
                if not taken:
                    continue
                items = [entry['finding'] for entry in taken]
                where = [home.get(item['label']) for item in items] if kind == 'comparison' \
                    else [named_part(self.plan, item.get('section')) for item in items]
                found = {'understanding': narrow['understanding'], 'findings': items} if kind == 'reading' else items
                report = self.repair(kind, found, where, narrow=True, numbers=[entry['number'] for entry in taken])
                sessions += report['sessions']
                response += report['response']
            narrow.update(step='settle', sessions=sessions, response=response)
            self.save()
        revised = [answer['finding'] for answer in narrow['response'] if answer['action'] == 'revised']
        kept = [{'number': answer['finding'], 'because': KEPT + answer['note']}
                for answer in narrow['response'] if answer['action'] == 'kept']
        if narrow['step'] == 'settle':
            if (changed() or narrow.get('typeset')) and not self.settle():
                # The text that was read passed these checks. The changes are given up, and the run goes on.
                failed = [item for item in self.open if item['check'] in (MACHINE, TYPESETTING)]
                self.open = [item for item in self.open if item not in failed]
                reason = FAILING + ' '.join(str(problem) for item in failed for problem in item['problems'])[:600]
                self.narrow_undo(before, kept + [{'number': number, 'because': reason} for number in revised])
            else:
                narrow['step'] = 'read'
                self.save()
        if narrow['step'] == 'read':
            tex, spans, _ = self.assemble()
            changes = self.changes(before, spans)
            left, undone = list(kept), {}
            if changes:
                verdicts = self.read_changes(tex, changes)
                made_for = {change['change']: set(verdict['findings']) for change, verdict in zip(changes, verdicts['changes'])}
                unsound = {verdict['change']: verdict['reason'] for verdict in verdicts['changes'] if not verdict['sound']}
                # The changes made for one finding are one answer to it: they are undone together.
                gone = set(unsound)
                while True:
                    reopened = set().union(*(made_for[number] for number in gone))
                    more = {number for number, findings in made_for.items() if findings & reopened} - gone
                    if not more:
                        break
                    gone |= more
                for number in sorted(reopened):
                    own = [reason for change, reason in unsound.items() if number in made_for[change]]
                    left.append({'number': number, 'because': UNDONE + ' '.join(own or unsound.values())})
                left += [{'number': verdict['finding'], 'because': UNANSWERED + verdict['reason']}
                         for verdict in verdicts['findings'] if not verdict['answered'] and verdict['finding'] not in reopened]
                for name in dict.fromkeys(change['part'] for change in changes):
                    here = [change for change in changes if change['part'] == name]
                    positions = {position for position, change in enumerate(here) if change['change'] in gone}
                    if positions:
                        undone[name] = with_passages_undone(before[name], self.parts[name], positions)
                self.event('changes', findings=revised,
                           changes=[{**{key: change[key] for key in ('change', 'part', 'lines')},
                                     **{key: verdict[key] for key in ('sound', 'findings', 'reason')}}
                                    for change, verdict in zip(changes, verdicts['changes'])],
                           answered=verdicts['findings'], undone=sorted(gone))
            else:
                left += [{'number': number, 'because': NO_CHANGE} for number in revised]
            self.narrow_undo(undone, left)
        if narrow['step'] == 'undo':
            folder = self.out / 'narrow' / 'undone'
            undone = {path.stem: read_file(path) for path in sorted(folder.glob('*.tex'))}
            if undone:
                # Settled also when the texts are already back, as in a run that was stopped after it put them back:
                # paper.tex and the PDF are then made from the parts as they stand.
                self.keep(undone)
                if not self.settle(0):
                    # Without the changes that were undone, the others no longer pass: all of them are given up.
                    failed = [item for item in self.open if item['check'] in (MACHINE, TYPESETTING)]
                    self.open = [item for item in self.open if item not in failed]
                    reason = FAILING + ' '.join(str(problem) for item in failed for problem in item['problems'])[:600]
                    back = {name: before[name] for name in changed()}
                    self.narrow_undo(back, kept + [{'number': number, 'because': reason} for number in revised])
                    self.keep(back)
                    if not self.settle(0):
                        return False
            narrow['step'] = 'done'
            self.save()
        return True

    def narrow_undo(self, texts, left):
        """Record what is to be put back and which findings stay open, before anything is put back.

        The texts are files in <out>/narrow/undone, so that a run that is stopped while it puts them back
        does so again from the same texts; the passages are counted on the parts as they stand now, and a
        part that was put back counts otherwise."""
        folder = self.out / 'narrow' / 'undone'
        if folder.exists():
            shutil.rmtree(folder)  # a text left here would be put back: the step `undo` reads every text of this folder
        folder.mkdir(parents=True)
        for name, text in texts.items():
            if text != self.parts[name]:
                write_text(folder / (name + '.tex'), text)
        self.narrow.update(step='undo', left=left)
        self.save()

    def changes(self, before, spans):
        """The passages in which the parts differ from the text that was read, in the order of the manuscript."""
        first = {name: start for name, start, _ in spans}
        answered = {answer['finding'] for answer in self.narrow['response'] if answer['action'] == 'revised'}
        changes = []
        for name, _, _ in spans:
            old, new = part_lines(before[name]), part_lines(self.parts[name])
            for i1, i2, j1, j2 in changed_passages(before[name], self.parts[name]):
                lines = f'after line {first[name] + j1 - 1}' if j1 == j2 \
                    else f'{first[name] + j1} to {first[name] + j2 - 1}' if j2 - j1 > 1 else str(first[name] + j1)
                changes.append({'change': len(changes) + 1, 'part': name, 'lines': lines, 'before': '\n'.join(old[i1:i2]),
                                'after': '\n'.join(new[j1:j2]),
                                'findings': sorted({number for session in self.narrow['sessions'] if name in session['changed']
                                                    for number in session['findings'] if number in answered})})
        return changes

    def read_changes(self, tex, changes):
        """The session that reads the changed passages; its verdicts on the changes and on the findings."""
        notes = {answer['finding']: answer['note'] for answer in self.narrow['response'] if answer['action'] == 'revised'}
        findings = [{'finding': entry['number'], 'check': entry['check'], 'reported': entry['finding'],
                     'repair': notes[entry['number']]} for entry in self.narrow['findings'] if entry['number'] in notes]
        numbers = [entry['finding'] for entry in findings]

        def read(output):
            verdicts = self.load(output / 'verdicts.json')
            judged, answered = verdicts.get('changes'), verdicts.get('findings')
            problems = []
            if not isinstance(judged, list) or [v.get('change') if isinstance(v, dict) else None for v in judged] \
                    != [change['change'] for change in changes] \
                    or not all(isinstance(v.get('sound'), bool) and isinstance(v.get('reason'), str)
                               and (v['sound'] or v['reason'].strip()) and isinstance(v.get('findings'), list)
                               and all(number in numbers for number in v['findings']) for v in judged):
                problems.append('output/verdicts.json: "changes" has one object for each change of changes.json, in their '
                                'order, with its "change", "sound" as true or false, "findings" as an array of numbers of '
                                'findings of changes.json, and a "reason", which is not empty when the change is not sound')
            if not isinstance(answered, list) or [v.get('finding') if isinstance(v, dict) else None for v in answered] \
                    != numbers or not all(isinstance(v.get('answered'), bool) and isinstance(v.get('reason', ''), str)
                                          and (v['answered'] or v.get('reason', '').strip()) for v in answered):
                problems.append('output/verdicts.json: "findings" has one object for each finding of changes.json, in their '
                                'order, with its "finding", "answered" as true or false, and a "reason", which is not empty '
                                'when the finding is not answered')
            if problems:
                raise Unusable(problems)
            return {'changes': [{'change': v['change'], 'sound': v['sound'], 'findings': sorted(set(v['findings'])),
                                 'reason': v['reason'].strip()} for v in judged],
                    'findings': [{'finding': v['finding'], 'answered': v['answered'], 'reason': v.get('reason', '').strip()}
                                 for v in answered]}

        files = {'paper.tex': tex, 'references.bib': self.materials['bibliography'],
                 'changes.json': json.dumps({'findings': findings, 'changes': changes}, ensure_ascii=False, indent=2) + '\n'}
        # Each reading of changes is a check of its own: a later one reads other changes and does not stand for it.
        about = 'changes ' + str(1 + sum(event['event'] in ('changes', 'not done') for event in self.log))
        checks = ' and of the '.join(sorted({entry['check'] for entry in findings}))
        verdicts = self.session('changes', CHANGES_PROMPT.format(reader=method_part(READER_SECTION)), files, read,
                                self.assessor,
                                check={about: f'the reading of the passages ({len(changes)}) that the last repair changed '
                                              f'for findings of the {checks}; the changes stay in the paper as the '
                                              'repair left them'})
        if verdicts is None:
            # Not made (session). The changes stay in the paper, and the record says that nobody read them.
            return {'changes': [{'change': change['change'], 'sound': True, 'findings': change['findings'], 'reason': ''}
                                for change in changes],
                    'findings': [{'finding': number, 'answered': True, 'reason': ''} for number in numbers]}
        return verdicts

    def narrow_end(self, covered=None):
        """Leave in the open list, of the findings that the repair took up, those that stay open, each with the reason.

        `covered` gives, for each section whose running text was compared with the elements once more
        after the repair (cover_again), what that comparison reported. It takes the place of what was
        open about the running text of those sections, since it speaks for their text as it stands
        now; a passage that was reported before and is reported again keeps the reason it was left with."""
        narrow = self.narrow
        left = {entry['number']: entry['because'] for entry in narrow.get('left', [])}
        taken = {(entry['check'], entry['position']): entry['number'] for entry in narrow['findings']}
        if narrow['step'] != 'done':
            # The manuscript was left failing, which the open list says by itself; the findings stay as they were.
            left = {number: left.get(number, 'the repair did not come to its end') for number in taken.values()}
        for item in self.open:
            if any(check == item['check'] for check, _ in taken):
                item['after_repairs'] += 1
                item['problems'] = [
                    problem if (item['check'], position) not in taken
                    else {**problem, 'open_because': left[taken[item['check'], position]]}
                    for position, problem in enumerate(item['problems'])
                    if (item['check'], position) not in taken or taken[item['check'], position] in left]
        if covered:
            def home(problem):
                part = named_part(self.plan, problem.get('section'))
                return self.plan['sections'][0]['id'] if part == 'abstract' else part

            reasons ={entry['finding'].get('quote'): left[entry['number']] for entry in narrow['findings']
                       if entry['check'] == COVERAGE and entry['number'] in left}
            item = next((item for item in self.open if item['check'] == COVERAGE), None)
            problems = [problem for problem in (item['problems'] if item else []) if home(problem) not in covered] \
                + [{**finding, 'open_because': reasons.get(finding['quote'], COVERED_AGAIN)}
                   for findings in covered.values() for finding in findings]
            self.open = [other for other in self.open if other['check'] != COVERAGE]
            self.open.append({'check': COVERAGE, 'after_repairs': item['after_repairs'] if item else 0, 'problems': problems})
        self.open = [item for item in self.open if item['problems']]
        self.narrow = None
        self.save()
        shutil.rmtree(self.out / 'narrow', ignore_errors=True)

    # -- the findings that a finished run left open ----------------------------------------------------------

    def listed(self):
        """The findings of the open list, in its order, each as (number, check, position in its item, the finding)."""
        found = [(item['check'], position, problem) for item in self.open for position, problem in enumerate(item['problems'])]
        return [(number, *entry) for number, entry in enumerate(found, 1)]

    def listing(self, lines):
        """The open findings for the user: numbered, each with the check it comes from and the place it points to."""
        say = lines.append
        does = {READING: 'a repair session changes the passage that the finding names, and a session reads what was changed',
                LIKENESS: 'a repair session changes the passage that the finding names, and a session reads what was changed',
                COMPARISON: 'a repair session corrects the statement, a session reads what was changed, and the statement '
                            'is compared with its element again',
                UNCOMPARED: 'the statement is compared with its element',
                COVERAGE: 'a repair session cuts the passage, rewords it so that it says no more than the element '
                          'named with it, or moves a derivation into the proof that uses it; a session reads what was '
                          'changed, and the running text of the section is compared with the elements again',
                WIDE:'the manuscript is typeset again and every line of a part that is too wide goes to repair, while '
                      'one in the title, a heading, the author line or the bibliography is text that no repair '
                      'changes and is reported again; this is done whenever a finding is acted on, since the '
                      'typesetting cannot tell these lines from new ones'}
        listed = self.listed()
        for item in self.open:
            say('')
            say(f"{item['check']}: {len(item['problems'])} open after {item['after_repairs']} repairs. Acting on one: "
                f"{does.get(item['check'], 'nothing')}.")
            for number, check, _, problem in listed:
                if check != item['check']:
                    continue
                if isinstance(problem, str):
                    say(f'  {number:3d}. {problem}')
                    continue
                if 'label' in problem:
                    say(f"  {number:3d}. {problem.get('number') or 'the statement'} with \\label{{{problem['label']}}}")
                else:
                    part = named_part(self.plan, problem.get('section'))
                    say(f"  {number:3d}. {collapsed(str(problem.get('where', '')))}"
                        f" [{'part ' + part if part else 'no single section'}]")
                for key in ('quote', 'problem', 'difference', 'open_because'):
                    if is_text(problem.get(key)):
                        say(f"       {key.replace('_', ' ')}: {shortened(collapsed(problem[key]), 320)}")
        return lines

    def act(self):
        """Act on the findings that a finished run left open and that the user chose; then the run ends anew.

        The statements that differ, the sentences that no element covers and, in a run made before the
        stage `resolve` existed, the findings of the readings go to a narrow repair, with the settling
        and the reading of its changes (narrow_run). Then the numbered statements whose text this
        changed, and the chosen ones that were never compared, are compared with their elements, once:
        a statement that differs then is reported as open and is not repaired in the same pass. Last,
        the running text of every section that the pass changed is compared with the elements once
        more (cover_again), whatever the pass changed it for, so that a pass which ends with nothing
        open leaves a manuscript whose running text was compared as it stands."""
        narrow = self.narrow
        passed = self.narrow_run()
        if passed:
            before = {name: read_file(self.out / 'narrow' / 'before' / (name + '.tex')) for name in self.parts}
            old = {found['label']: found['text'] for found in found_statements(self.plan, before)}
            tex, spans, rows = self.assemble()
            rows = [row for row in rows if row['comparison']['verdict'] == 'not compared'
                    and (row['label'] in narrow['uncompared'] or old.get(row['label']) != row['paper_statement'])]
            if rows:
                self.compare_rows(rows, tex, spans)
        # The statements that differ, for their present text. One that was not taken up, and whose text is as it
        # was, stands as it stood; the others say why they are open.
        _, _, rows = self.assemble()
        reasons = {entry['number']: entry['because'] for entry in narrow.get('left', [])}
        taken = {entry['finding']['label']: reasons.get(entry['number']) for entry in narrow['findings']
                 if entry['check'] == COMPARISON}
        item = next((item for item in self.open if item['check'] == COMPARISON), None)
        known = {problem['label']: problem for problem in item['problems']} if item else {}
        differing = []
        for row in rows:
            if row['comparison']['verdict'] != 'differs':
                continue
            label, difference = row['label'], row['comparison']['difference']
            if label in known and label not in taken and known[label]['difference'] == difference:
                differing.append(known[label])
            else:
                differing.append({'label': label, 'difference': difference, 'open_because': taken.get(label) or DIFFERS_NOW})
        if item:
            item.update(after_repairs=item['after_repairs'] + bool(taken), problems=differing)
        elif differing:
            self.open.append({'check': COMPARISON, 'after_repairs': 0, 'problems': differing})
        narrow['findings'] = [entry for entry in narrow['findings'] if entry['check'] != COMPARISON]
        self.narrow_end(self.cover_again() if passed else None)
        if passed:
            self.place()  # where the elements without a number stand, for the text as this pass left it

    # -- what the bounded repairs left open, closed without a person -------------------------------------

    def close(self):
        """Close what a run that came to its end left open, by means that are certain to end; False as narrow_run.

        A run leaves open what its bounded repairs did not settle, and a person can act on that with
        --open-findings. A caller that has nobody to ask calls this instead. Nothing in it is repeated:

          statements  every numbered statement whose present text has no verdict is compared, once. A
                      statement that differs from its element, now or by the comparisons of the run, is
                      restated as its element says it (restate) and compared once more. The verdict of
                      that comparison is recorded, and nothing follows it.
          text        every passage of running text that no element covers is taken out of the
                      manuscript (remove). A deletion asserts nothing, so nothing compares the text
                      for its sake.
          last        a numbered statement that a repair of the LaTeX changed after this is compared,
                      once, and a line that is still wider than the text block is recorded. The
                      running text of every section that a repair of the LaTeX changed during the
                      pass is compared with the elements, once (cover_repaired); a passage that no
                      element covers then is recorded and stays.

        What was done is in `closed`, which the last `end` event of the log carries: for each passage
        that was removed its text and the element that came nearest, for each statement that was
        restated its text before and after, the difference, and the verdict after, and for each
        passage that the last comparison of the running text reported what that comparison says of
        it. A statement is restated once in a run. The open list is then empty, unless the manuscript
        is left failing its machine checks or its typesetting, or holds findings of the readings,
        which only a run made before the stage `resolve` existed leaves open."""
        tex, spans, rows = self.assemble()
        fresh = [row for row in rows if row['comparison']['verdict'] == 'not compared']
        if fresh:
            self.compare_rows(fresh, tex, spans)
            _, _, rows = self.assemble()
        before = {entry['label'] for entry in self.closed if entry['kind'] == 'restated'}
        differing = [row for row in rows if row['comparison']['verdict'] == 'differs' and row['label'] not in before]
        if differing and not self.restate(differing):
            return False
        # A restatement is recorded before its text is in place (restate). Here it receives the text and the verdict
        # that its statement has now, also when the pass that made it was stopped before the comparison.
        now = {row['label']: row for row in self.assemble()[2]}
        with self.lock:
            for entry in self.closed:
                if entry['kind'] == 'restated' and entry['verdict'] == 'not compared' and entry['label'] in now:
                    row = now[entry['label']]
                    entry.update(after=row['paper_statement'], verdict=row['comparison']['verdict'],
                                 difference_after=row['comparison'].get('difference', ''))
            self.open = [item for item in self.open if item['check'] not in (COMPARISON, UNCOMPARED)]
            self.save()
        item = next((item for item in self.open if item['check'] == COVERAGE), None)
        if item:
            removed = self.remove(item['problems'])
            if removed is None:
                return False
            with self.lock:
                self.closed += removed
                self.open = [other for other in self.open if other['check'] != COVERAGE]
                self.save()
        tex, spans, rows = self.assemble()
        # One whose comparison was not made in this pass (session) is recorded as such and is not tried once more.
        late = {row['label']: row for row in rows
                if row['comparison']['verdict'] == 'not compared' and 'not_done' not in row['comparison']}
        if late:
            self.closed += [{'kind': 'differs', 'label': verdict['label'], 'number': late[verdict['label']]['number'],
                             'element': late[verdict['label']]['element'], 'difference': verdict['difference']}
                            for verdict in self.compare_rows(list(late.values()), tex, spans)
                            if verdict['verdict'] == 'differs']
        wide = next((item for item in self.open if item['check'] == WIDE), None)
        # The lines that are too wide now take the place of those that the list already holds: a pass that was stopped
        # after it had recorded them, in the check of the places, is made again on a manuscript that was settled anew.
        self.closed = [entry for entry in self.closed if entry['kind'] != 'wide'] \
            + [{'kind': 'wide', 'problem': problem} for problem in (wide['problems'] if wide else [])]
        self.open = [item for item in self.open if item['check'] != WIDE]
        self.save()
        self.cover_repaired()  # what a repair of the LaTeX wrote during this pass, compared with the elements once
        self.place()  # where the elements without a number stand, for the text as this pass left it
        self.assemble()
        return True

    def restate(self, rows):
        """One session restates numbered statements as their elements say them; False when that leaves the manuscript failing.

        The session has, for each statement, the statement of its element in words and in Lean and the
        difference that the comparison found. It changes these statements and their proofs and nothing
        else, which the script checks: each of them has another text, every other numbered statement
        has the text it had, and the running text is as it was, so that what was compared with the
        elements stands. Each restatement is entered in `closed` before the parts are replaced, with
        the text before and the difference; `close` adds the text and the verdict after. The
        manuscript is then checked by machine and typeset, and the restated statements are compared
        with their elements once."""
        tex, spans, _ = self.assemble()
        labels = [row['label'] for row in rows]
        stated = lambda parts: {found['label']: found['text'] for found in found_statements(self.plan, parts)
                                if found['label']}
        running = lambda parts: [entry['text'] for entries in running_text(self.plan, parts, spans).values()
                                 for entry in entries if entry['kind'] == 'running text']
        old, text = stated(self.parts), running(self.parts)

        def read(output):
            parts = written_parts(output, self.parts)
            new = {**self.parts, **parts}
            now = stated(new)
            problems = [f'the statement with \\label{{{label}}} has the text it had; restate it as its element says it'
                        for label in labels if now.get(label) == old.get(label)]
            problems += [f'the statement with \\label{{{label}}} is gone, or is no numbered statement any more'
                         for label in old if label not in now]
            problems += [f'the statement with \\label{{{label}}} was changed, and statements.json does not list it'
                         for label in old if label not in labels and label in now and now[label] != old[label]]
            if running(new) != text:
                problems.append('text outside the numbered statements and the proofs was changed; change the listed '
                                'statements and their proofs, and nothing else')
            if problems:
                raise Unusable(problems)
            return {name: content for name, content in parts.items() if content != self.parts[name]}

        entries = [{**{key: row[key] for key in ('label', 'number', 'element', 'record_statement', 'lean_statement',
                                                 'paper_statement')}, 'difference': row['comparison']['difference']}
                   for row in rows]
        files = {'paper-method.md': method_before_checks(), 'paper.tex': tex,
                 'statements.json': json.dumps(entries, ensure_ascii=False, indent=2) + '\n',
                 'records.md': render_records(self.materials, self.plan, {row['element'] for row in rows}, self.layout),
                 **{name: content for name, content in self.records().items() if name.startswith('elements')},
                 **{f'parts/{name}.tex': content for name, content in self.parts.items()}}
        lines = '; '.join(f'lines {a} to {b} are `parts/{name}.tex`' for name, a, b in spans)
        changed = self.session('restate', RESTATE_PROMPT.format(spans='Its ' + lines + '.'), files, read, self.writer,
                               attempts=CLOSING_ATTEMPTS)
        with self.lock:
            # Recorded before the parts are replaced, so that a pass stopped after this still says which statements
            # were restated, from which text and for which difference.
            self.closed += [{'kind': 'restated', 'label': row['label'], 'number': row['number'], 'element': row['element'],
                             'before': row['paper_statement'], 'difference': row['comparison']['difference'],
                             'after': '', 'verdict': 'not compared', 'difference_after': ''} for row in rows]
            self.save()
            self.keep(changed)
        self.event('restated', statements=labels, changed=sorted(changed))
        if not self.settle():
            return False
        tex, spans, after = self.assemble()
        again = [row for row in after if row['label'] in labels and row['comparison']['verdict'] == 'not compared']
        if again:
            self.compare_rows(again, tex, spans)
        return True

    def remove(self, problems):
        """One session takes the passages that no element covers out of the manuscript; what was done, or None.

        `problems` are findings of the comparison of the running text, each with the passage it quotes.
        The session deletes the passages and mends the text around them. The script checks what it
        returns on the text that the comparison is made on (running_text): no quoted passage stands in
        it any more, which for a formula of a proof means that nothing outside the proof refers to it;
        every numbered statement is as it was, so that its verdict stands; and every changed passage is
        shorter than it was, so that nothing was put in the place of what went. A passage that does not
        stand in the text, as after a pass that was stopped once the parts were kept, needs no session.
        The manuscript is then checked by machine and typeset. None when that leaves it failing."""
        tex, spans, _ = self.assemble()
        compared = lambda parts: collapsed(' '.join(entry['text'] for entries in
                                                    running_text(self.plan, parts, spans).values() for entry in entries))
        stated = lambda parts: [(found['label'], found['text']) for found in found_statements(self.plan, parts)]
        standing, old = compared(self.parts), stated(self.parts)
        present = [problem for problem in problems if collapsed(problem['quote']) in standing]
        changed = {}
        if present:
            def read(output):
                parts = {name: content for name, content in written_parts(output, self.parts).items()
                         if content != self.parts[name]}
                new = {**self.parts, **parts}
                found = compared(new)
                faults = [f'the passage {number} of removals.json still stands in the text, or its formula is still '
                          'referred to from outside its proof' for number, problem in enumerate(present, 1)
                          if collapsed(problem['quote']) in found]
                if stated(new) != old:
                    faults.append('a numbered statement was changed, moved or removed; leave every numbered statement '
                                  'exactly as it is')
                for name in parts:
                    was, has = part_lines(self.parts[name]), part_lines(new[name])
                    for i1, i2, j1, j2 in changed_passages(self.parts[name], new[name]):
                        earlier, later = collapsed(' '.join(was[i1:i2])), collapsed(' '.join(has[j1:j2]))
                        if later != earlier and len(later) >= len(earlier):
                            faults.append(f'a passage of parts/{name}.tex is not shorter than it was, so something stands '
                                          'in the place of what was deleted, or text was changed that the list does not '
                                          'concern: ' + shortened(later, 200))
                if not parts:
                    faults.append('no part was changed: write the complete new text of each part you change as '
                                  'output/<name>.tex, with the file name it has in parts/')
                if faults:
                    raise Unusable(faults)
                return parts

            removals = [{'number': number, 'part': named_part(self.plan, problem.get('section')),
                         **{key: problem.get(key, '') for key in ('where', 'quote', 'asserts', 'nearest')}}
                        for number, problem in enumerate(present, 1)]
            files = {'paper.tex': tex, 'removals.json': json.dumps(removals, ensure_ascii=False, indent=2) + '\n',
                     **{f'parts/{name}.tex': content for name, content in self.parts.items()}}
            lines = '; '.join(f'lines {a} to {b} are `parts/{name}.tex`' for name, a, b in spans)
            changed = self.session('remove', REMOVE_PROMPT.format(spans='Its ' + lines + '.'), files, read, self.writer,
                                   attempts=CLOSING_ATTEMPTS)
            self.keep(changed)
        self.event('removed', passages=[problem['quote'] for problem in problems], changed=sorted(changed))
        if changed and not self.settle():
            return None
        return [{'kind': 'removed', **{key: problem.get(key, '') for key in ('where', 'section', 'quote', 'asserts',
                                                                           'nearest', 'difference')},
                 **({'source': problem['source']} if 'source' in problem else {})}  # a sentence about a cited work
                for problem in problems]

    # -- a run that is continued, and a run that is only looked at ----------------------------------------

    def recorded_draft(self):
        """The draft that a run from a draft (--from-draft) recorded in <out> when it began; None for any other run.

        The materials of such a run hold the declarations that closed a gap of this draft, so every
        later reading of the materials takes them from here and not from the folder the draft came from."""
        begun = next((event for event in self.log if event['event'] == 'materials'), {})
        path = self.out / 'draft.json'
        return read_json(path) if begun.get('from_draft') and path.is_file() else None

    def further(self, model):
        """The declarations that the materials of this run hold beside what the proof of the root rests on."""
        return closing(self.sketched, model) if self.sketched else []

    def take_up(self):
        """What <out> holds of a run that was stopped: the plan with its account, the parts, the state of the stages."""
        out = self.out
        state = read_json(out / 'state.json') if (out / 'state.json').is_file() else {}
        if (state.get('resolve') or {}).get('step') == 'place' and not self.dry:
            # The run was stopped while the parts and the plan of the stage `resolve` were put in place.
            self.place_resolution()
        held = sorted(path.stem for path in (out / 'parts').glob('*.tex')) if (out / 'parts').is_dir() else []
        study = read_file(out / 'study.md') if (out / 'study.md').is_file() else ''
        self.sketched = self.sketched or self.recorded_draft()
        if (out / 'plan.json').is_file() and study.strip():
            plan = read_json(out / 'plan.json')
            problems = check_plan(self.materials, plan, [entry['key'] for entry in self.collection])
            if not problems:
                self.take_plan(plan, study)
            elif held:
                raise Stop(f'{out / "plan.json"} does not pass the check of the plan, and parts were written from it, so '
                           'the run cannot be continued; start a new one in a new folder. The check found: ' + '; '.join(problems))
        elif held:
            raise Stop(f'{out} holds parts and no plan with its account (plan.json, study.md) from which they were '
                       'written, so the run cannot be continued; start a new one in a new folder')
        if self.plan is None:
            return
        sections = self.plan['sections']
        self.parts.update(written_parts(out / 'parts', ['abstract'] + [section['id'] for section in sections]))
        if not self.written(sections[0]):  # the introduction and the abstract are written by one session, or not at all
            for name in ('abstract', sections[0]['id']):
                self.parts.pop(name, None)
        if state:
            self.readings = state['readings']
            # The stages are complete for the parts that were all written. When a section is still to be written,
            # nothing that was read or compared holds for the manuscript that will come of it.
            if all(self.written(section) for section in sections):
                self.done, self.open, self.rewritten, self.compared = (state[key] for key in ('done', 'open', 'rewritten', 'compared'))
                self.narrow, self.kept, self.resolving = state.get('narrow'), state.get('kept', []), state.get('resolve')
                self.closed, self.placed = state.get('closed', []), state.get('placed')

    def preview(self, lines):
        """What the run would do next and what its sessions would be given, without launching one or writing a file."""
        say = lines.append
        if self.plan is None:
            files = self.planning_kit()
            under = lambda folder: (lambda name: name.startswith(folder))
            say('The next session plans the paper. It would be given, in bytes:')
            for words, wanted in (
                    ('materials-digest.md, which it reads in full', lambda name: name == 'materials-digest.md'),
                    ('paper-method.md and user-writing-preferences.md', lambda name: name in ('paper-method.md', 'user-writing-preferences.md')),
                    ('exemplars.md, the list of the collection', lambda name: name == 'exemplars.md'),
                    (f"exemplars/, {sum(map(under('exemplars/'), files))} papers, of which it reads the {CHOSEN_PAPERS} it chooses",
                     under('exemplars/')),
                    (f"elements/, {sum(map(under('elements/'), files))} records, which it opens as a decision needs them",
                     under('elements/'))):
                say(f'  {size(files, wanted):9d}  {words}')
            say('The sections are written after the plan, and their briefs are made from it.')
        else:
            sections = self.plan['sections']
            todo = [section['id'] for section in sections if not self.written(section)]
            say(f"The plan is there and passes the check: {len(sections)} sections, {len(self.plan['statements'])} numbered "
                f"statements, {len(self.plan['notation'])} entries of notation.")
            say('Parts that are written: ' + (', '.join(name for name in self.parts) or 'none') + '.')
            if todo:
                say('Sections that are still to be written, ' + ('the introduction first and the others '
                                                                 if todo[0] == sections[0]['id'] and len(todo) > 1 else '')
                    + f'up to {self.parallel} at a time: ' + ', '.join(todo) + '.')
            elif self.narrow is not None:
                step = 'compare' if self.narrow['step'] == 'done' else self.narrow['step']
                say(f"Every section is written. The run was stopped in the last repair of {len(self.narrow['findings'])} "
                    f'findings, at the step "{step}" of repair, settle, read, undo'
                    + (' and compare; it would be continued there, and then end.' if self.narrow.get('pass')
                       else '; it would be continued there, and the stages after it would run.'))
            else:
                done = [name for name, _ in STAGES if name in self.done]
                say('Every section is written. The manuscript would be settled, and then the stages after the writing would '
                    'run' + (', of which these are complete: ' + ', '.join(done) if done else '') + '.')
            say('What a session that writes or repairs a section would be given, in bytes. "read" is what its prompt has it '
                'read in full: the brief, the method, the writing preferences, the account of the papers and the papers of '
                'the section, and for the introduction root.md. "beside" is what it opens when it needs it: root.md for '
                'the other sections, plan.json, references.bib, elements.md and elements/.')
            say(f"  {'section':14s} {'brief':>8s} {'elements':>8s} {'by statement':>12s} {'papers':>8s} {'read':>8s} {'beside':>8s}")
            for number, section in enumerate(sections):
                files = self.kit(section)
                aside = lambda name: (name.startswith('elements') or name in ('plan.json', 'references.bib')
                                      or (name == 'root.md' and number > 0))
                say(f"  {section['id']:14s} {size(files, lambda name: name == 'brief.md'):8d} {len(self.layout.full[section['id']]):8d} "
                    f"{len(self.layout.cited[section['id']]):12d} {size(files, lambda name: name.startswith('exemplars/')):8d} "
                    f"{size(files, lambda name: not aside(name)):8d} {size(files, aside):8d}")
        return lines


@contextmanager
def stops_recorded(run):
    """The work of a run that is begun or taken up: when it stops, the log receives the `end` event of a run that
    failed, and the stop goes on to the caller."""
    try:
        yield
    except Stop as exc:
        run.event('end', status='failed', error=str(exc))
        raise


def produce(instance, out, tex=None, choice=None, parallel=PARALLEL, resume=False, dry=False,
            draft=False, from_draft=None, title_page=None, gate=None, main=None):
    """The whole command for a new paper, or with `resume` for one whose run was stopped; returns the exit code.

    With `dry` it makes every check that comes before the first session, launches nothing and writes
    nothing, and prints what the run would do next. With `draft` it plans the paper, makes its draft
    and ends (Paper.draft). `from_draft` is the folder of such a draft, from which the paper is then
    written without a new planning of it (Paper.plan_from_draft). A run that is continued is the kind
    of run it was begun as, whether or not these are given again. `title_page` is the file that names
    the authors, and `gate` a semaphore that bounds the sessions of this run together with those of
    whoever shares it (Sessions).

    `main` names the theorem that the paper is built around when that is not the declaration that
    settles the root (extract). A run records it in its materials and a draft in draft.json. A run that
    is continued, and a paper that is written from a draft, take the main result from that record;
    when `main` is given to them as well it has to name the same element, and the command refuses
    another. Without `main`, and when it names the settling declaration, a new run is what it is
    without this parameter."""
    out = Path(out)
    if draft and from_draft:
        raise Stop('--draft makes the draft of a paper and --from-draft writes the paper from one; a run is one of the two')
    if resume:
        if not (out / 'materials.json').is_file():
            raise Stop(f'{out} holds no run of this command to continue: it has no materials.json')
    elif out.exists() and any(out.iterdir()):
        raise Stop(f'{out} is not empty; give a new folder to --out, or --resume to continue the run it holds, or '
                   '--typeset-only to typeset the manuscript it holds')
    model = replay(instance)
    settling_proof(model)  # refuses before anything is written
    chosen = chosen_main(model, main)  # and so does a main result that is no settled formal theorem
    authors = read_title_page(title_page) if title_page else None  # a file that cannot be used stops the run here
    codes = read_classification(title_page) if title_page else []
    given = read_draft(from_draft) if from_draft and not resume else None  # and so does a folder that holds no draft
    if dry:
        # A paper that is missing is fetched by a run, over the network; a dry run names it and fetches nothing.
        (manifest, papers, wrong), fetched = unfetched_collection(), None
    else:
        manifest, papers, fetched = load_collection()  # stops, before anything is written, when papers stay missing
    run = Paper(instance, out, tex, choice or {}, parallel, dry, gate)
    run.collection, run.papers = manifest, papers
    # A paper that is written from a draft has among its materials the declarations that closed a gap of the
    # draft. A run that is continued takes them from the draft it recorded when it began, so that the materials
    # are those of materials.json whatever has become of the folder the draft came from.
    run.sketched = given[2] if given else run.recorded_draft() if resume else None
    # The main result that a run is made around is recorded: by a run in its materials, by a draft in draft.json.
    # A run that is continued and a paper that is written from a draft take it from that record. Given again,
    # it has to be the same, because everything that exists so far was made around the recorded one.
    if resume or run.sketched is not None:
        stored = read_json(out / 'materials.json') if resume else {}
        recorded = (stored['main'] if 'settles' in stored else None) if resume else run.sketched.get('main')
        if main is not None and chosen != recorded:
            raise Stop((f'the run in {out}' if resume else f'the draft in {from_draft}') + ' was made with '
                       + (f'the main result {recorded}' if recorded else 'the declaration that settles the root as its '
                          'main result') + f', and this run was given --main {main}; give the same main result, or none')
        chosen = recorded
    materials = extract(instance, model, run.further(model), chosen)
    said = ['Dry run: no session is launched and nothing is written.'] if dry else []
    if dry and wrong:
        said.append('Papers of the collection that are missing or differ from its manifest, which a run would fetch: '
                    + ', '.join(wrong) + '.')
    if resume:
        ended = last_end(run.log)
        if ended is not None:
            raise Stop(f"the run in {out} came to its end ({ended['status']}); there is nothing to continue. "
                       + ('Its draft is draft.json, beside plan.json and study.md' if ended['status'] == 'draft'
                          else '--typeset-only typesets the manuscript it holds'))
        # The run is continued as what it was begun as, which its first event says.
        begun = next((event for event in run.log if event['event'] == 'materials'), {})
        if (draft and not begun.get('draft')) or (from_draft and not begun.get('from_draft')):
            raise Stop(f'the run in {out} was not begun with ' + ('--draft' if draft else '--from-draft')
                       + '; continue it with --resume alone')
        draft, from_draft = bool(begun.get('draft')), from_draft or begun.get('from_draft')
        run.materials = read_json(out / 'materials.json')
        same_canon(out, run.materials, materials, 'the run cannot be continued')
        run.take_up()
        said.append(f"The materials of the canon are those of materials.json: {len(run.materials['elements'])} elements.")
        said += chosen_said(run.materials)
        run.event('resume', plan=run.plan is not None, parts=list(run.parts), done=dict(run.done), parallel=run.parallel)
    else:
        run.materials = materials
        said.append(f"The materials: {len(materials['elements'])} elements that the formal proof of the root rests on.")
        said += chosen_said(materials)
        lost = sorted({e['source'] for e in materials['elements'] if e['source']} - set(materials['bibliography_keys']))
        if not dry:
            run.out.mkdir(parents=True, exist_ok=True)
            write_json(run.out / 'materials.json', run.materials)
            write_text(run.out / 'materials.md', render_materials(run.materials))
            if run.sketched:
                write_json(run.out / 'draft.json', run.sketched)  # beside the materials that were taken with it
        run.event('materials', root=run.materials['root']['name'], state=run.materials['root']['state'],
                  settled_by=settling(run.materials), elements=[e['name'] for e in run.materials['elements']],
                  **({'main': run.materials['main']} if 'settles' in run.materials else {}),
                  tex=run.recipe[0] if run.recipe else None, parallel=run.parallel,
                  warnings=[f'the source {key} of an element is not in bibliography.bib' for key in lost],
                  **({'draft': True} if draft else {}),
                  **({'from_draft': str(Path(from_draft).resolve()), 'further': run.materials.get('further', [])}
                     if from_draft else {}))
        run.event('collection', folder=str(EXEMPLARS), papers=[entry['key'] for entry in manifest], fetched=fetched)
    if authors is not None:
        run.authors, run.codes = authors, codes
        if not dry:
            write_json(run.out / 'title-page.json', {'authors': authors, **({'msc2020': codes} if codes else {})})
    if dry:
        if draft:
            said.append('This run makes the draft of the paper: after the plan, each section is sketched and the '
                        'sketched statements are compared with their elements, and the run ends with draft.json.')
        if from_draft and run.plan is None:
            said.append(f'The paper is written from the draft in {from_draft}: its plan is brought to these materials '
                        'by script, and a planning session is launched only when the check of the plan then finds '
                        'problems. What follows describes a planning session of a run without a draft.')
        print('\n'.join(run.preview(said)))
        return 0
    with stops_recorded(run):
        if run.narrow is not None and run.narrow.get('pass'):
            run.act()  # the run had come to its end and was stopped while it acted on findings it had left open
        else:
            if run.plan is None:
                if from_draft:
                    run.plan_from_draft(from_draft)
                else:
                    run.make_plan(draft)
            if draft:
                return run.draft()
            run.write_parts()
            run.after_writing()
    return run.finish()


def chosen_said(materials):
    """What the command says of a main result that is not the declaration that settles the root; nothing otherwise."""
    return [f"The main result of the paper is {materials['main']}; the declaration that settles the root is "
            f"{materials['settles']}."] if 'settles' in materials else []


def ended_run(instance, out, tex, choice, parallel, dry, gate):
    """A run that came to its end with findings left open, loaded to be acted on: the run and its `end` event.

    The run has the open list of that event, its plan and its parts, and the materials it was made
    from. Stop when the folder holds no such run, when it ended with its manuscript failing, and
    when the canon is no longer what the run began with."""
    out = Path(out)
    if not all((out / name).is_file() for name in ('materials.json', 'plan.json', 'state.json', 'log.json')):
        raise Stop(f'{out} holds no run of this command that came to its end (materials.json, plan.json, state.json, log.json)')
    run = Paper(instance, out, tex, choice or {}, parallel, dry, gate)
    ended = last_end(run.log)
    if ended is None:
        raise Stop(f'the run in {out} has not come to its end, so it has no list of open findings to act on: the last '
                   'event of its log.json is not the end of a run. A run that is going comes to its end by itself; '
                   'a run that was stopped is continued with --resume')
    left = json.loads(json.dumps(ended['open']))
    if any(item['check'] in (MACHINE, TYPESETTING) for item in left):
        raise Stop(f'the run in {out} ended before its readings and its comparison were made, because the machine checks '
                   'or the typesetting stayed open; --open-findings acts on what the comparisons of a run that came to '
                   'its end left open')
    if not left:
        raise Stop(f"the run in {out} came to its end with no finding left open ({ended['status']}); there is nothing "
                   'to act on')
    model = replay(instance)
    settling_proof(model)
    run.collection, run.papers, _ = unfetched_collection() if dry else load_collection()
    run.materials = read_json(out / 'materials.json')
    run.sketched = run.recorded_draft()
    # The materials are taken as the run took them: with the declarations of its draft, around its main result.
    same_canon(out, run.materials, extract(instance, model, run.further(model),
                                           run.materials['main'] if 'settles' in run.materials else None),
               'its open findings cannot be repaired from the records as they are now')
    run.take_up()
    if run.plan is None or not all(run.written(section) for section in run.plan['sections']):
        raise Stop(f'{out} does not hold the plan and every part of the manuscript whose findings its log lists')
    run.open = left
    return run, ended


def act_on_open(instance, out, tex=None, choice=None, parallel=PARALLEL, numbers='all', dry=False):
    """Take up a run that came to its end with findings left open, and act on them; returns the exit code.

    The open findings are those of the last event of the log, which is the `end` of the run. With `dry`
    they are listed with their numbers and nothing else is done. Otherwise those whose numbers
    `numbers` names, or all of them, are acted on as Paper.act describes, and the run ends anew; the
    findings that were not chosen stay open as they were. The run is continued with --resume when it
    is stopped. As for --resume, the canon has to be what the run began with, since the repair
    sessions work from the records."""
    run, ended = ended_run(instance, out, tex, choice, parallel, dry, None)
    listed = run.listed()
    if dry:
        # A finding quotes texts of sessions, and output that is redirected is encoded as the system's locale has it.
        # A character that encoding lacks is printed as an escape instead of ending the command (depmap.say).
        depmap.say('\n'.join(run.listing([
            'Dry run: no session is launched and nothing is written.',
            f"The run in {out} came to its end ({ended['status']}) with {len(listed)} findings left open. --open-findings "
            'acts on all of them; followed by numbers of this list, as in --open-findings 2,5-7, it acts on those, and '
            'the others stay open as they are.'])))
        return 0
    chosen = set(chosen_numbers(numbers, len(listed)))
    run.event('open findings', chosen=sorted(chosen), listed=len(listed), parallel=run.parallel)
    understanding = next((event['understanding'] for event in reversed(run.log) if event['event'] == 'reading'), None)
    run.narrow_begin(chosen=[(number, check, position) for number, check, position, _ in listed
                             if number in chosen and check in NARROW_KINDS],
                     understanding=understanding,
                     **{'pass': True, 'typeset': any(number in chosen and check == WIDE for number, check, _, _ in listed),
                        'uncompared': [problem['label'] for number, check, _, problem in listed
                                       if number in chosen and check == UNCOMPARED]})
    with stops_recorded(run):
        run.act()
    return run.finish()


def last_end(log):
    """The `end` event with which the run of a log came to its end, or None when the run did not.

    A run came to its end when the last event of its log is an `end` whose status is not `failed`. The log
    of a run that was stopped ends with another event, and that of a run that failed with an `end` of that
    status. --resume, --open-findings and the finalize pipeline (finalize.Run.paper_run) decide by this
    rule what to do with the run that a folder holds."""
    return log[-1] if log and log[-1].get('event') == 'end' and log[-1].get('status') != 'failed' else None


def left_failing(ended):
    """Whether a run ended with its manuscript failing the machine checks or the typesetting after their repairs.

    Such a run ended before its readings and its comparisons were complete, and nothing takes it up."""
    return any(item['check'] in (MACHINE, TYPESETTING) for item in ended.get('open') or [])


def close_open(instance, out, tex=None, choice=None, parallel=PARALLEL, gate=None):
    """Take up a run that came to its end with findings left open, and close them without a person; the exit code.

    What the comparisons left open is closed as Paper.close describes: a numbered statement that
    differs from its element is restated as the element says it, and a passage of running text that
    no element covers is taken out of the manuscript. The run then ends anew, and its `end` event
    carries what was done under `closed`. The exit code is 2 only when the manuscript is left
    failing its machine checks or its typesetting. A caller that conducts a run with nobody to ask
    uses this where a person would use --open-findings. A pass that was stopped is taken up by
    --resume, which ends the run with what is still open, and then by this function again."""
    run, _ = ended_run(instance, out, tex, choice, parallel, False, gate)
    run.event('closing', open=[{'check': item['check'], 'problems': len(item['problems'])} for item in run.open],
              parallel=run.parallel)
    with stops_recorded(run):
        run.close()
    return run.finish()


def typeset_only(instance, out, tex=None, choice=None, parallel=PARALLEL, title_page=None):
    """Typeset the manuscript a previous run left in `out`, with the same checks and repairs.

    The run that wrote the manuscript has to have carried its reading and its comparison to their end,
    since typesetting does not repeat them, and what that comparison left open stays open. A numbered
    statement that a repair made here changes is not compared again, and `finish` reports it as open.
    `title_page` is a file that names the authors; the manuscript is then typeset with that author
    line, and without it with the one the folder already holds."""
    out = Path(out)
    needed = [out / 'materials.json', out / 'plan.json', out / 'parts' / 'abstract.tex']
    if not all(path.is_file() for path in needed):
        raise Stop(f'{out} does not hold a manuscript of this command (materials.json, plan.json, parts/)')
    authors = read_title_page(title_page) if title_page else None
    codes = read_classification(title_page) if title_page else []
    run = Paper(instance, out, tex, choice or {}, parallel)
    if run.recipe is None:
        raise Stop('no TeX command is available: none of ' + ', '.join(ENGINES) + ' is on PATH, and --tex was not given')
    # The first end in the log that is not a failure is that of the run that wrote the manuscript; a run that was
    # stopped and continued has its failures before it. The machine checks and the typesetting are made again
    # here, and nothing else is.
    produced = next((event for event in run.log if event['event'] == 'end' and event.get('status') != 'failed'), {})
    left = produced.get('open', [])
    if produced.get('status') not in ('complete', 'no_tex', 'open_findings') \
            or any(item['check'] in (MACHINE, TYPESETTING) for item in left):
        raise Stop(f'{out} holds a manuscript whose reading and comparison did not run to their end; --typeset-only '
                   'typesets only a manuscript that an earlier run finished apart from the typesetting')
    # What is open now is what the last end that is not a failure lists: --open-findings may have acted on what the
    # run left. The machine checks and the typesetting are made again here, so what they left before is not kept.
    latest = next(event for event in reversed(run.log) if event['event'] == 'end' and event.get('status') != 'failed')
    run.open = [item for item in latest.get('open', []) if item['check'] not in (MACHINE, TYPESETTING)]
    run.kept = list(latest.get('kept', []))
    run.closed = list(latest.get('closed', []))
    run.materials = read_json(out / 'materials.json')
    run.take_plan(read_json(out / 'plan.json'), read_file(out / 'study.md') if (out / 'study.md').is_file() else '')
    run.sketched = run.recorded_draft()  # the briefs of a repair carry the drafted statements, as before
    if authors is not None:
        run.authors, run.codes = authors, codes
        write_json(out / 'title-page.json', {'authors': authors, **({'msc2020': codes} if codes else {})})
    run.parts = {name: read_file(out / 'parts' / (name + '.tex')) for name in ['abstract'] + [s['id'] for s in run.plan['sections']]}
    if (out / 'correspondence.json').is_file():
        run.compared = {row['label']: {**row['comparison'], 'sha256': row['paper_statement_sha256']}
                        for row in read_json(out / 'correspondence.json')['statements']
                        if row['comparison']['verdict'] != 'not compared'}
    if (out / 'state.json').is_file():
        state = read_json(out / 'state.json')
        if state.get('narrow'):
            raise Stop(f'the run in {out} was stopped in the last repair of findings and the reading of its changes; '
                       'continue it with --resume before the manuscript is typeset')
        run.done, run.readings, run.rewritten = state['done'], state['readings'], state['rewritten']
        run.placed = state.get('placed')
    run.event('typeset only', tex=run.recipe[0])
    with stops_recorded(run):
        run.settle()
    return run.finish()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('instance', type=Path)
    parser.add_argument('--out', type=Path, required=True,
                        help='the folder that receives the paper; new or empty, or with --resume the folder of the run')
    parser.add_argument('--resume', action='store_true', help='continue the run that --out holds, from what it has on disk')
    parser.add_argument('--parallel', type=int, default=PARALLEL, metavar='N',
                        help=f'sessions that run side by side where the work allows it; default {PARALLEL}')
    parser.add_argument('--dry-run', action='store_true',
                        help='launch no session and write nothing: check what comes before the first session and print '
                             'what the run would do next and what its sessions would be given')
    parser.add_argument('--model', help='<provider>/<model> for every session, the readings and the comparison included; '
                                        'default: the first of the instance\'s models for planning, writing and repair, '
                                        'and the first model of the review role for the readings and the comparison')
    parser.add_argument('--effort', help='the effort of planning, writing and repair, and of every session when --model '
                                         'is given; default: that of the instance\'s first model, and, for the readings '
                                         'and the comparison without --model, that of the review role\'s first model')
    parser.add_argument('--typeset-only', action='store_true', help='typeset the manuscript that --out already holds')
    parser.add_argument('--open-findings', nargs='?', const='all', metavar='NUMBERS',
                        help='take up the run that --out holds, which came to its end with findings left open, and act '
                             'on them: on all, or on those whose numbers follow, as in 2,5-7. With --dry-run: list the '
                             'open findings with their numbers')
    parser.add_argument('--draft', action='store_true',
                        help='make the draft of the paper and no paper: the plan, and for each section the numbered '
                             'statements as the paper will state them, the formulas used as results and the gaps, '
                             'compared with the elements; --out receives plan.json, study.md and draft.json')
    parser.add_argument('--from-draft', type=Path, metavar='FOLDER',
                        help='write the paper from the draft that FOLDER holds (plan.json, study.md, draft.json): its '
                             'plan is brought to this instance by script, and the sections are written with the '
                             'drafted statements')
    parser.add_argument('--title-page', type=Path, metavar='FILE',
                        help='a JSON file {"authors": [{"name", "address", "email"}]} with the authors of the paper, '
                             'and optionally "msc2020", the codes of its subject classification; without it, or '
                             'with an empty list, the manuscript has no author line')
    parser.add_argument('--main', metavar='DECLARATION',
                        help='the theorem of the instance that the paper is built around, when that is not the '
                             'declaration that settles the root: a settled formal theorem, as a rule one from which '
                             'the root follows. The paper then states it as its main theorem and the root as a '
                             'numbered statement beside it')
    parser.add_argument('--tex', nargs=argparse.REMAINDER, help='the TeX command; takes the rest of the command line')
    args = parser.parse_args(argv)
    try:
        options = {'--out', '--model', '--effort', '--typeset-only', '--resume', '--parallel', '--dry-run',
                   '--open-findings', '--draft', '--from-draft', '--title-page', '--main'}
        if args.tex is not None and (not args.tex or options & set(args.tex)):
            raise Stop('--tex takes the rest of the command line: name a command after it, and put it last')
        if args.parallel < 1:
            raise Stop('--parallel is the number of sessions that run side by side, at least 1')
        if args.typeset_only and (args.resume or args.dry_run):
            raise Stop('--typeset-only typesets a finished manuscript; it goes with neither --resume nor --dry-run')
        if args.open_findings is not None and (args.typeset_only or args.resume):
            raise Stop('--open-findings takes up a run that came to its end; it goes with neither --typeset-only nor '
                       '--resume. A pass over open findings that was stopped is continued with --resume alone')
        if (args.draft or args.from_draft or args.main) and (args.typeset_only or args.open_findings is not None):
            raise Stop('--draft, --from-draft and --main belong to a run that is begun or continued; they go with '
                       'neither --typeset-only nor --open-findings, which keep the main result of the run they take up')
        if args.title_page and args.open_findings is not None:
            raise Stop('--title-page goes with a run and with --typeset-only; --open-findings keeps the author line that '
                       'the folder holds')
        choice = {'model': args.model, 'effort': args.effort}
        # A dry run writes nothing, so it may be given beside a command that is at work in the folder; no other may.
        with nullcontext() if args.dry_run else alone(args.out):
            if args.open_findings is not None:
                return act_on_open(args.instance, args.out, args.tex, choice, args.parallel, args.open_findings,
                                   args.dry_run)
            if args.typeset_only:
                return typeset_only(args.instance, args.out, args.tex, choice, args.parallel, args.title_page)
            return produce(args.instance, args.out, args.tex, choice, args.parallel, args.resume, args.dry_run,
                           args.draft, args.from_draft, args.title_page, main=args.main)
    except (Stop, OSError, ValueError) as exc:
        # After the reason, what the person does next where the reason alone does not say it (Stop.todo). Such a stop
        # comes from a session, so the folder holds a run, and this command is started again with --resume.
        todo = getattr(exc, 'todo', None)
        print('paper.py: ' + str(exc) + (f'\n{todo} This command is started again with --resume and the same --out.'
                                         if todo else ''), file=sys.stderr)
        return 1


if __name__ == '__main__':
    contain_session_processes()  # whatever a session starts ends with this command
    raise SystemExit(main())
