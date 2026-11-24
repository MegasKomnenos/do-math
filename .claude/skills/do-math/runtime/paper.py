"""Write the paper of an instance whose root is settled by a formal proof.

    python paper.py <instance> --out <folder> [--resume] [--parallel <n>] [--dry-run]
                    [--model <provider/model>] [--effort <effort>] [--typeset-only]
                    [--open-findings [<numbers>]] [--tex <command...>]

One command produces the paper to the end without stopping for the user. What the sessions it
launches do not decide is fixed in ../reference/paper-method.md, which they receive. The stages:

  materials    everything the formal proof of the root rests on is taken from the canon, and the
               collection of real papers in ../exemplars is checked against its manifest (fetch.py
               is run once for papers that are missing or differ)
  plan         a session reads a digest of the materials, which gives every element by its
               statement and has the full record of each beside it as a file of its own; it
               chooses the papers of the collection this paper is written like, reads them, writes
               an account of how they are written, and decides how each element appears in the
               paper, which notation the paper uses, and which two of the chosen papers each
               section is written beside; the script checks the plan
  write        one session per section writes its LaTeX. Each has a brief for its section, made by
               the script: its part of the plan, the records of its own elements in full, and the
               statements of the elements of other sections that those name. It reads the account
               of the papers and the two papers of its section. The introduction is written first;
               the other sections are written side by side, up to --parallel at a time
  settle       the script assembles paper.tex, checks it by machine and typesets it, and typesets
               it once more, in typeset/displays, only to measure which displayed formulas have
               less room than they need; what fails goes to repair sessions, and the manuscript is
               assembled and checked again
  reading      a session that has only the manuscript reads it as the paper's reader, and repair
               sessions take up what it found; the manuscript is read again after each repair
               but the last, which is narrow and of which only the changes are read (see below)
  likeness     a session that has the manuscript and four papers the plan did not choose reports
               where the manuscript is written otherwise than they are; repair sessions take up
               what it found, until two such readings in succession find nothing. When the bound
               of these readings is reached first, the repair after the last of them is narrow
  rereading    when a repair after a reading beside real papers rewrote the manuscript, it is read
               by itself again as under "reading": a rewriting for manner can change a proof
  comparison   for each section a session compares its numbered statements with the statements of
               their elements, the sections side by side; when a repair of what they found changed
               the manuscript, the manuscript is read by itself again before the statements are
               compared once more

Every loop is bounded by the constants below. A repair is made section by section: what a check or
a reader found in one section goes to a session that has that section's brief and changes that
section only, and these sessions run side by side; what concerns no single section goes to one
session that may change every part, after the others. Each session runs in its own folder under
<out>/sessions with its prompt and the files it is given, and the script reads the files the prompt
asked for.

A repair may rewrite, and a rewriting can lose a step of a proof, so the text that a repair leaves
is read. After every reading but the last of its stage, the next reading does that. The repair
after the last reading is followed by no reading of the whole manuscript, so it is made narrowly,
and what it changed is read:

  repair   the repair sessions are told to change the passages that their findings name and
           nothing else
  settle   the manuscript is assembled, checked by machine and typeset, as after every repair
  read     one session has the manuscript and every passage that differs from the text which the
           last reading read, each with its text before and after. It reads each where it stands
           and says whether the change is sound (no step lost, no statement changed in what it
           says, notation and references consistent with the rest), for which findings it was
           made, and for each finding whether the changes answer it
  undo     a change found unsound is put back as it was read, and with it the other changes made
           for the same findings; the manuscript is checked and typeset once more, without
           repairs. When the manuscript fails its checks here or under "settle", every change
           of the repair is put back

No further round follows. Every passage of the manuscript is then text that the last reading read,
or a change that was found sound. A finding that stays open says why under "open_because": the
repair session kept the text, or its change was undone, or its change is sound and stays and does
not answer the finding. Such a repair is not a rewriting for the stage "rereading", which follows
the repairs that may rewrite. The statements are compared after it, in the stage "comparison".

<out> receives paper.tex, references.bib, paper.pdf, plan.json, correspondence.json (which element
each numbered statement states; never inside the paper), materials.md and log.json (what was
launched and what each check found). The work stays beside them: materials.json, study.md (the
planning session's account of how the chosen papers are written), parts/ (the abstract and the
sections as they stand), state.json, sessions/ and typeset/, and narrow/ while a narrow repair is
under way (the parts as they were read, and the texts that are put back). --typeset-only does not
use the collection.

Everything a later step needs is in <out> as soon as it exists, so a run that was stopped is
continued with --resume and the same --out. The materials are taken from the canon again and have to
be those of materials.json; a plan that is there and passes the check is used; a part that is there
is not written again; and state.json says which of the stages after the writing are complete, with
what the later ones need from them. A stage that was interrupted is made again from its start, on
the parts as they stand. The one exception is a run that was stopped inside a narrow repair or the
reading of its changes: state.json records the step it was in and the findings, and the run goes on
at that step, without making the readings before it again; a repair that was stopped is made again
from the parts as they were read. Without --resume, <out> is new or empty.

--open-findings takes up a run that came to its end with findings left open (exit code 2) and acts
on them in one pass. With --dry-run it lists the open findings of the last `end` event of log.json,
numbered, each with the check it comes from and the place it points to, and launches nothing.
Without numbers it acts on all of them; followed by numbers of that list, as in
--open-findings 2,5-7, it acts on those, and the others stay open as they were. The findings of the
readings and of the comparison go to a narrow repair with its settling and the reading of its
changes, as above. Then the numbered statements whose text the pass changed, and the chosen ones
that were never compared, are compared with their elements, once: a statement that differs then is
reported as open and is not repaired in the same pass. A line wider than the text block is not
taken up finding by finding: the settling sends every such line to repair whenever the pass changed
a part or such a line was chosen, because the typesetting cannot tell an old wide line from a new
one. The pass ends with a new `end` event. It needs the canon to be what the run began with, as
--resume does, and a pass that was stopped is continued with --resume.

--parallel is the number of sessions that run side by side where the work allows it: the sections
after the introduction, the repairs of different sections, the comparisons of different sections.
--dry-run launches no session and writes nothing: it makes every check that comes before the first
session, and prints what the run would do next and how large the files are that its sessions would
be given.

--tex takes the rest of the command line, so it comes last. It names tectonic, latexmk or pdflatex,
which are run in the way each needs, or any other command, which is run once in the folder of the
manuscript with `paper.tex` appended and has to leave paper.pdf. Without --tex the first of the
three found on PATH is used. When there is none, everything except the typesetting is done and the
command says so; --typeset-only later typesets the manuscript that <out> already holds.

Exit codes: 0 the paper is complete; 1 refused or failed; 2 produced with findings left open
(log.json names them); 3 the manuscript is complete and no TeX command was available.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, wait
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
import time

from canon import BIB_ENTRY, Canon, declaration_text, read_question_account, read_record, sha256_text
from cli_adapter import detect_usage_limit, provider_for_model
from knowledge import ROOT_QUESTION, STANDINGS, refuting_proofs, replay
from launch import worker_command, worker_environment
import runtime_support
from runtime_support import contain_session_processes, popen_options, read_json
from settings import load_settings

REFERENCE = Path(__file__).resolve().parents[1] / 'reference'
METHOD = REFERENCE / 'paper-method.md'
PREFERENCES = REFERENCE / 'user-writing-preferences.md'
READER_SECTION = 'The reader'  # the part of the method that the reading session receives, and nothing else of it
# The part of the method that a reading beside real papers receives, and nothing else of it.
LIKENESS_SECTION = 'Reading the manuscript beside real papers'
EXEMPLARS = Path(__file__).resolve().parents[1] / 'exemplars'  # the collection: manifest.json, <key>.tex, fetch.py
MANIFEST_FIELDS = ('key', 'arxiv', 'title', 'authors', 'journal', 'year', 'category', 'field', 'pages', 'licence',
                   'abstract', 'sha256', 'why')

PLAN_ATTEMPTS = 3      # planning sessions before the command gives up on a plan it can carry out
SESSION_ATTEMPTS = 2   # sessions of any other kind before it gives up on output it can read
REPAIR_ROUNDS = 3      # repair sessions for one round of machine checks and typesetting
READING_ROUNDS = 3     # independent readings at one time; the repair after the last one is narrow (narrow_run)
CHOSEN_PAPERS = 6      # papers of the collection the plan chooses for the paper to be written like
SECTION_PAPERS = 2     # of those, the papers the plan names for one section; its writer reads them whole
PARALLEL = 4           # sessions side by side, unless --parallel says otherwise; a session mostly waits on the network
LIKENESS_PAPERS = 4   # papers the plan did not choose, given to one reading beside real papers
LIKENESS_ROUNDS = 8    # readings beside real papers at the most
LIKENESS_CLEAN = 2     # readings in succession without a departure that end those readings
COMPARISON_ROUNDS = 2  # comparisons of the statements; a repair follows every one but the last
LIMIT_WAITS = 12       # times one session is started again after the account's usage limit
TEX_SECONDS = 600      # one TeX command
FETCH_SECONDS = 3600   # one run of the collection's fetch.py
WIDE_PT = 5.0          # a line this many points wider than the text block is sent back to be broken
WIDE = 'lines wider than the text block'
UNCOMPARED = 'numbered statements whose present text was not compared with their elements'
READING = 'reading of the manuscript by itself'
LIKENESS = 'reading of the manuscript beside real papers'
COMPARISON = 'comparison of the numbered statements with their elements'
MACHINE = 'machine checks of the manuscript'
TYPESETTING = 'typesetting'
# The checks whose findings a repair session can take up one by one, each with the kind of repair that does. The last
# repair that a reading receives, and every repair of findings that a finished run left open, is a narrow one: it
# changes the passages its findings name, and a session then reads the passages it changed (Paper.narrow_run).
NARROW_KINDS = {READING: 'reading', LIKENESS: 'likeness', COMPARISON: 'comparison'}
# Why a finding is open after the last repair it received, as the open list says it under "open_because".
KEPT = 'the repair session kept the text: '
UNDONE = 'changed, and the change was undone, because the reading of the changed passages found it unsound: '
UNANSWERED = 'changed, and the reading of the changed passages found that the change does not answer the finding; the change stays: '
FAILING = ('changed, and every change of this repair was undone, because the manuscript did not pass its machine checks '
           'or could not be typeset with them: ')
NO_CHANGE = 'the repair session reported a change, and the manuscript does not differ from the text that was read'
ONCE_CONFIRMED = ('repaired after the reading that reported it; the one reading that followed found no departure, and '
                  'the readings ended at their bound before a second reading confirmed that')
DIFFERS_NOW = ('the statement was changed by a repair of open findings, and the comparison that followed found this '
               'difference')
# The stages after the writing whose completion state.json records, in their order; each is a method of Paper.
STAGES = (('reading', 'read_and_repair'), ('likeness', 'read_beside_papers'), ('rereading', 'read_again'),
          ('comparison', 'compare'))

ENGINES = ('tectonic', 'latexmk', 'pdflatex')
NUMBERED = ('theorem', 'proposition', 'lemma', 'corollary', 'definition')
ENVIRONMENT = re.compile(r'\\begin\{(' + '|'.join(NUMBERED) + r')\}(.*?)\\end\{\1\}', re.S)
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
LABEL_FORM = re.compile(r'[a-z]+:[a-z0-9-]+')
OVERFULL = re.compile(r'Overfull \\hbox \(([0-9.]+)pt too wide\) '
                      r'(?:detected at line (\d+)|in (?:paragraph|alignment) at lines (\d+)--(\d+))')

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


# runtime_support builds every file it writes in one buffer that the whole process shares, which suits the single
# thread of the runner. This command runs sessions side by side in threads, so each of its writes, and the launch
# helper that writes the settings of a session, takes this lock; a file is then whole whoever else is writing.
WRITING = threading.RLock()


def write_text(path, content):
    with WRITING:
        runtime_support.write_text(path, content)


def write_json(path, value):
    with WRITING:
        runtime_support.write_json(path, value)


class Stop(Exception):
    """The command cannot go on; the message says why."""


class Unusable(Exception):
    """A session left output the script cannot use; the problems go to the session that is started in its place."""

    def __init__(self, problems):
        super().__init__('; '.join(problems))
        self.problems = list(problems)


def is_text(value):
    return isinstance(value, str) and bool(value.strip())


def read_file(path):
    return Path(path).read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def method_part(title):
    """One section of the method document, by its heading."""
    match = re.search(r'^## ' + re.escape(title) + r'\n(.*?)(?=^## |\Z)', read_file(METHOD), re.M | re.S)
    if not match:
        raise Stop(f'{METHOD} has no section "{title}"')
    return match[1].strip()


# ----------------------------------------------------------------------------- the collection of real papers

KEY_FORM = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.+-]*')


def collapsed(text):
    """The text with every run of whitespace replaced by one space."""
    return re.sub(r'\s+', ' ', text).strip()


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
            done = subprocess.run([sys.executable, str(fetch)], cwd=EXEMPLARS, stdin=subprocess.DEVNULL,
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
    """The declaration whose formal proof settles the root: a proof of the root, or of its negation."""
    elements, root = model['elements'], model['root']
    if model['root_state'] == 'formal_proved':
        found = [p for p in elements[root]['proofs'] if elements[p]['settled'] and elements[p]['formal']]
    elif model['root_state'] == 'formal_refuted':
        found = refuting_proofs(model, elements[root]['statement_of'], formal=True)
    else:
        raise Stop(f"the root is {model['root_state']}; the paper is written once the root is settled by a formal "
                   'proof (formal_proved or formal_refuted)')
    return found[0]


def extract(instance, model):
    """Everything the paper is written from: what the formal proof of the root rests on, with the records.

    The elements are those reached from the settling proof through what each proof names and each
    statement mentions. A statement with several proofs is followed through the declaration that
    the proof above it names, so the other proofs and what only they rest on stay out. The order is
    one of dependence: an element comes after everything it names or mentions."""
    instance = Path(instance)
    canon = Canon(instance)
    index = canon.load_index()['entries']
    elements = model['elements']
    main = settling_proof(model)

    def below(name):
        return sorted({u for u in elements[name]['uses'] + elements[name]['statement_uses'] if u in elements})

    order, seen, stack = [], {main}, [(main, iter(below(main)))]
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
        return item

    understanding, review = read_question_account(canon, ROOT_QUESTION)
    bibliography = read_file(canon.bibliography) if canon.bibliography.is_file() else ''
    root = model['root']
    root_sections = sections_of(root)
    return {'revision': model['sequence'], 'root': {
                'name': root, 'state': model['root_state'], 'words': read_file(instance / 'root.md').strip(),
                'lean': elements[root]['statement'], 'statement': root_sections.get('Statement'),
                'explanation': root_sections.get('Explanation')},
            'main': main, 'axioms': elements[main]['axioms'], 'allowed_axioms': model['allowed_axioms'],
            'understanding': understanding.strip(), 'understanding_review': review,
            'elements': [entry(name) for name in order],
            'bibliography': bibliography, 'bibliography_keys': BIB_ENTRY.findall(bibliography),
            'identifiers': sorted(set(elements) | {e['module'] for e in elements.values()})}


def backquoted(values):
    return ', '.join('`' + value + '`' for value in values) or '(nothing)'


def head_lines(materials):
    """The root, how it was settled, and the account of the problem as a whole, as lines of a text."""
    root = materials['root']
    proved = root['state'] == 'formal_proved'
    lines = ['## The root', '', 'The root in words, as it was fixed when the research began:', '',
             *('> ' + line for line in root['words'].splitlines()), '',
             'The root in Lean:', '', '```lean', 'theorem ' + root['lean'], '```', '',
             ('The root has been proved' if proved else 'The root has been refuted') + ' by a formal proof. '
             + (f"The declaration whose formal proof settles it is `{materials['main']}`"
                + ('.' if proved else ', whose statement is the negation of the root.')),
             'Axioms that formal proof depends on: ' + (', '.join(materials['axioms']) or 'none')
             + '. Axioms the instance allows: ' + ', '.join(materials['allowed_axioms']) + '.', '']
    if materials['main'] != root['name']:
        for title, key in (("The statement in the root's record", 'statement'), ("The explanation in the root's record", 'explanation')):
            if root[key]:
                lines += [f'**{title}.**', '', root[key], '']
    lines += ['## The understanding so far of the problem as a whole', '',
              materials['understanding'] or 'No account of the problem as a whole has been written.', '']
    if materials.get('understanding_review'):
        lines += ['### Review of the change that supplied this account', '', materials['understanding_review'], '']
    return lines


RECORD = (('Description', 'description'), ('Statement', 'statement'), ('Explanation', 'explanation'), ('Proof', 'proof'),
          ('Literature', 'literature'))


def element_lines(element, keys=None, users=True):
    """One element as lines of a text, from the line that gives its kind: the Lean form, what it names, its record.

    `keys` are the sections of the record that are given; without it, all of them. Without `users` the
    elements that name this one are left out; a brief says in its own way where an element is used."""
    lines = [f"{element['kind']} · weight: {element['weight']}"
             + (f" · short name: {element['short']}" if element['short'] else '')
             + (' · the main result' if element['main'] else ''), '']
    if element['kind'] == 'definition':
        lines += ['```lean', element['definition_text'], '```', '']
    else:
        lines += ['```lean', 'theorem ' + element['lean'], '```', '']
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
        if element[key] and (keys is None or key in keys):
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
             + (' · the main result' if element['main'] else '')
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
             f"{len(materials['elements'])} elements in dependence order: each comes after everything its statement "
             'mentions and its proof names, and the last is the main result.', '']
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
              f"{len(files)} elements in dependence order: each comes after everything its statement mentions and its "
              'proof names, and the last is the main result. Each line gives the name, the kind, the weight, the short '
              'name where the record has one, and the file that holds the full record.', '']
    found = {'root.md': '\n'.join(['# The root and the account of the problem', '', note, '',
                                    *head_lines(materials)]).rstrip('\n') + '\n'}
    for element in materials['elements']:
        listed.append(f"- `{element['name']}` · {element['kind']} · {element['weight']}"
                      + (f" · {element['short']}" if element['short'] else '')
                      + (' · the main result' if element['main'] else '') + f" · `{files[element['name']]}`")
        found[files[element['name']]] = '\n'.join([f"# `{element['name']}`", '', *element_lines(element)]).rstrip('\n') + '\n'
    found['elements.md'] = '\n'.join(listed) + '\n'
    return found


def render_digest(materials):
    """The materials for the session that plans the paper: every element by what it says, and the proof as a whole.

    The planning session decides how each element appears in the paper, for which it needs what each
    element says and what it rests on. The explanations and the proofs in words are most of the
    materials; they are left to the files of the elements, and their lengths are given here. Two
    records are given in full, because the account of the whole proof is in them: the root's, and that
    of the declaration that settles the root."""
    files = element_files(materials)
    main = next(element for element in materials['elements'] if element['main'])
    lines = ['# Digest of the materials for the paper', '', lean_names_note(materials), '',
             'This digest gives every element that the proof of the root rests on by what it says: its name, its kind '
             'and its weight, its short name, its Lean form, what it names and what names it, its description and its '
             'statement in words. It leaves out the explanation and the proof in words of each element and gives their '
             'lengths in characters instead, and it leaves out the standing of each proof, which is the same for all: '
             'everything here is settled by a formal proof. The full record of every element is in a file of its own, which the digest '
             'names at the element. The record of the declaration that settles the root is given in full, before the '
             'list of the elements.', '',
             *head_lines(materials),
             '## The declaration that settles the root, with its record in full', '',
             f"### `{main['name']}`", '', *element_lines(main),
             '## The elements the proof rests on', '',
             f"{len(materials['elements'])} elements in dependence order: each comes after everything its statement "
             'mentions and its proof names, and the last is the main result.', '']
    for number, element in enumerate(materials['elements'], 1):
        lengths = [f'{title} in words: {len(element[key])} characters' if element[key] else f'no {title} in words'
                   for title, key in (('explanation', 'explanation'), ('proof', 'proof'))]
        lines += [f"### {number}. `{element['name']}`", '', *summary_lines(element),
                  f"Full record: `{files[element['name']]}` ({'; '.join(lengths)})."
                  + (' It is given in full above.' if element['main'] else ''), '']
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
    order = {section.get('id'): number for number, section in enumerate(sections)}
    if len(order) != len(sections):
        bad('two sections have the same id')
    # The titles stand in the manuscript as the plan has them, and a repair keeps the plan. A Lean name or the
    # word Lean in a title is therefore reported here, where a planning session can still change it.
    pattern = identifier_pattern(materials['identifiers'])
    titles = [('the title', plan.get('title')), ('the short title', plan.get('short_title'))] \
        + [(f"the title of section {s.get('id')!r}", s.get('title')) for s in sections]
    for where, title in titles:
        if is_text(title):
            plain = title.replace('\\_', '_')
            found = sorted({m[0] for m in pattern.finditer(plain)} | {m[0] for m in LEAN_WORDS.finditer(plain)})
            if found:
                bad(f'{where} has ' + ', '.join(found) + '; the paper names no declaration of the canon and does not '
                    'mention Lean (method, section "The implementation does not show")')
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


def shortened(text, length=120):
    """A text on one line, cut to a length that a list can carry."""
    text = collapsed(text)
    return text if len(text) <= length else text[:length].rsplit(' ', 1)[0] + ' ...'


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


def render_brief(materials, plan, section, layout=None):
    """brief.md: what the session that writes or repairs one section works from, made from the plan and the materials.

    It holds the section's part of the plan and what of the plan every section needs; the records in
    full of the section's own elements, in dependence order; and, by their statements, the elements of
    other sections that those name, each with the place where the paper has it and the notation under
    which the paper knows it."""
    layout = layout or Layout(materials, plan)
    sid, elements = section['id'], layout.elements
    full, cited = layout.full[sid], layout.cited[sid]
    lines = [f"# Brief for the section \"{section['title'].strip()}\"", '',
             f"Made by script, for the section whose id in the plan is `{sid}`, from the plan of the paper and from what "
             f"the proof of the root rests on, as the canon had it at revision {materials['revision']}. A name between "
             f"backquotes, such as `{materials['main']}`, is the name of a Lean declaration. It identifies an element here, "
             'in `plan.json` and in `elements/`, and it does not appear in the paper.', '',
             '## The paper', '', 'Title: ' + plan['title'].strip(), '',
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
                     + f" · {element['short'] or shortened(element['description'] or '')} · `{item['element']}`")
    lines += ['', '## What the plan puts into this section', '', collapsed(section['content']), '', *layout.assignment(sid), '',
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


def assemble(plan, parts):
    """paper.tex from the parts, in the order of the plan, and the lines each part occupies in it."""
    cites = any(CITE.search(uncommented(text)) for text in parts.values())
    title = plan['title'].strip()
    # The manuscript names no author. amsart then takes the title for the running head of the even pages and
    # puts it in capitals a second time, the letters of its formulas included. The head is set here instead,
    # from the short title when the plan gives one.
    lines = (PREAMBLE + '\\newcommand{\\RunningHead}{' + plan.get('short_title', title).strip()
             + '}\n\\uppercasenonmath\\RunningHead\n\\begin{document}\n\\title{' + title
             + '}\n\\begin{abstract}').split('\n')
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


def machine_findings(materials, plan, parts):
    """What a machine can check in the manuscript: each finding with the part in which it is to be corrected.

    A finding is {"part", "problem"}. "problem" is a sentence for a repair session. "part" is the name
    of a part, or None when the finding concerns no single part: the title, which the plan holds."""
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
            if element['source'] not in [k.strip() for m in CITE.finditer(here['text']) for k in m[1].split(',')]:
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
        if item['treatment'] == 'cited' and key not in [k.strip() for m in CITE.finditer(uncommented(parts[item['section']]))
                                                        for k in m[1].split(',')]:
            bad(item['section'], f"part {item['section']}: the plan cites the result with the bibliography key {key} "
                'here, and the part does not')
    # Labels and citations resolve. A label the plan gives to a section is that section's: when it is defined twice
    # the other part gives it up, and when it is missing the part that owes it is the one to correct.
    owner = {item['label']: item['section'] for item in plan['statements']}
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
        for key in sorted({k.strip() for m in CITE.finditer(plain) for k in m[1].split(',')} - keys):
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


def machine_checks(materials, plan, parts):
    """What a machine can check in the manuscript, as sentences for a repair session; empty when all hold."""
    return [finding['problem'] for finding in machine_findings(materials, plan, parts)]


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


def typeset(folder, recipe):
    """Run the TeX commands in the folder; returns the errors of the run, or nothing when paper.pdf was made."""
    folder = Path(folder)
    (folder / 'paper.pdf').unlink(missing_ok=True)
    cites = bool(CITE.search(uncommented(read_file(folder / 'paper.tex'))))
    for command in recipe:
        bibtex = Path(command[0]).stem.lower() == 'bibtex'
        if bibtex and not cites:
            continue  # BibTeX fails on a paper that cites nothing
        try:
            done = subprocess.run(command, cwd=folder, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, timeout=TEX_SECONDS, **popen_options())
        except subprocess.TimeoutExpired:
            return [f'{command[0]} did not finish within {TEX_SECONDS} seconds']
        except OSError as exc:
            raise Stop(f'{command[0]} could not be started: {exc}')
        output = done.stdout.decode('utf-8', errors='replace').replace('\r\n', '\n')
        with (folder / 'typeset.log').open('a', encoding='utf-8', newline='\n') as stream:
            stream.write('$ ' + ' '.join(command) + '\n' + output + '\n')
        if done.returncode and not (bibtex and done.returncode == 1):  # BibTeX returns 1 for warnings
            log = folder / 'paper.log'
            text = (log.read_text(encoding='utf-8', errors='replace') if log.is_file() else '') + '\n' + output
            lines = text.splitlines()
            starts = [i for i, line in enumerate(lines) if line.startswith('!') or re.match(r'\S*:\d+: ', line)
                      or 'error:' in line.lower()][:10]
            errors = ['\n'.join(lines[i:i + 5]) for i in starts] or ['\n'.join(lines[-30:])]
            return [f"{' '.join(command)} ended with exit code {done.returncode}", *errors]
    if not (folder / 'paper.pdf').is_file():
        return ['the TeX command ended without an error and left no paper.pdf']
    return []


def wide_lines(log):
    """The lines that TeX set wider than the text block by more than WIDE_PT, as its log reports them.

    TeX reports such a line as a warning and typesets the paper all the same, with the line standing
    out into the margin."""
    log = Path(log)
    if not log.is_file():
        return []
    found = []
    for width, single, first, last in OVERFULL.findall(log.read_text(encoding='utf-8', errors='replace')):
        if float(width) > WIDE_PT:
            where = f'line {single}' if single else f'lines {first} to {last}'
            found.append(f'paper.tex, {where}: TeX set a line {float(width):.0f}pt wider than the text block')
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
    reports as too wide is left to `wide_lines`. When the second typesetting fails, nothing is reported: the
    manuscript itself was typeset, and this measurement adds to that and decides nothing about it."""
    folder = Path(folder)
    measured = folder / 'displays'
    measured.mkdir(exist_ok=True)
    write_text(measured / 'paper.tex',
               read_file(folder / 'paper.tex').replace('\\begin{document}', DISPLAY_ROOM + '\\begin{document}', 1))
    if (folder / 'references.bib').is_file():
        shutil.copyfile(folder / 'references.bib', measured / 'references.bib')
    if typeset(measured, recipe):
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

METHOD_FILE = '''- `paper-method.md` is the method that every session follows. It fixes who the paper is for, what each of \
its parts does, which elements become numbered statements, the order, what of the canon the paper leaves out, and the \
manner of writing. Read it in full before anything else. Its decisions are made; your work applies them to this research.'''

PREFERENCES_FILE = '''- `user-writing-preferences.md` describes the writing that the person who will read the paper first \
prefers, with the occasions on which the preferences came to light. The method says how it bears on a paper.'''

PLAN_PROMPT = CONTEXT + '''

This session plans the paper. The sessions after it write the sections from the plan, side by side and without seeing \
each other's text, and the script holds the manuscript to the plan.

In this folder:
''' + METHOD_FILE + '''
- `materials-digest.md` is a digest of everything the proof of the root rests on. It holds the root in words and in Lean \
with its record; the account of the problem as a whole; the record in full of the declaration whose formal proof settles \
the root; then every element in dependence order, with its name, kind and weight, its short name, its Lean form, what it \
names and what names it, its description and its statement in words, and the lengths of its explanation and of its proof \
in words; and the bibliography. With the files of the next entry it is the only source of the mathematics and of the \
literature. Read it in full.
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

- "exemplars": the keys of the ''' + str(CHOSEN_PAPERS) + ''' papers you chose, all different, exactly as \
`exemplars.md` gives them.
- "title": the title of the paper.
- "short_title": the title in a shorter form, for the running head. The head is one line of small capitals at the top \
of every page, beside the page number, and it has room for about fifty-five letters and spaces. Leave the key out when \
the title itself is no longer than that. A head that does not fit is not printed, and the pages then carry their \
numbers alone.
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
empty for an entry that denotes no element, and a definition is named in one entry only.

The notation carries more than it would in a paper written by one hand. The sections are written side by side, so a \
writer never sees how another section names an object, and the plan is the only place where two writers can agree. Give \
an entry to every object that more than one section speaks of: the objects of the problem, and equally every auxiliary \
function, quantity, set, constant or condition that is defined in one section and used in another, or used in the proofs \
of two sections. This includes objects that the materials do not hold as a definition, such as a quantity that several \
records introduce in passing. An object that one section alone uses needs no entry, and its writer names it. The brief \
that each writer receives shows, at every element of another section that its own elements name, the entry under which \
the paper knows that element; a writer who finds none there has to invent a name, and two writers invent two.

When the plan absorbs a definition into several places that lie in different sections, the first of them in the order \
of the paper defines the object, and the later ones use it under its entry in the notation.

The script accepts the plan when every element of the materials appears in it exactly once; when kinds, labels, sections \
and reasons have the form above; when the main result is a theorem stated in the first section before every other \
theorem, proposition, lemma and corollary; when no statement mentions an object that is defined in a later numbered \
definition, and no proof comes before a numbered statement it rests on; when an element absorbed into a numbered \
statement is one that statement or its proof rests on; when only results with a source in the literature are cited; \
when an element that is not stated has in its place an element its proof names, another proof of the same statement, or \
the definition it is stated to agree with; when "exemplars" names ''' + str(CHOSEN_PAPERS) + ''' different keys \
of `exemplars.md` and every section names ''' + str(SECTION_PAPERS) + ''' different ones of them; and when every \
definition of the materials that the writers of two sections meet, because their elements state it, absorb it, name it \
or mention it, is named in "elements" of an entry of "notation". That last check sees only the definitions of the \
materials; for every other object the notation rests on your reading. A plan that fails goes to a new planning session \
with the list of failures.

Write also `output/study.md`: your account of how the chosen papers are written, as that section describes it, in \
free text. Every session that writes or repairs receives it, and it is all that such a session has of the papers you do \
not name for its section. So where the papers differ by the kind of section, say what each kind does: how introductions \
are built, how a section of preliminaries, a section that carries a long computation, and a section that proves the main \
theorem open, proceed and close.

Use no source other than the files in this folder. Write no part of the paper itself.
'''

BRIEF_FILE = '''- `brief.md` is what this section {tense} written from. The script made it from the plan and from the records of \
the research. It holds the outline of the proof and the sections of the paper; the notation; the numbered statements of the \
whole paper with their labels; what the plan puts into this section; the records in full of this section's elements, in an \
order in which each comes after what it depends on; and, for every element of another section that those name, what it \
says, where the paper has it, and the symbol or name under which the paper knows it. It is the source of the mathematics \
of this section. Read it in full.'''

RESEARCH_FILES = '''- `root.md` holds the root in words and in Lean, the record of the root, and the account of the \
problem as a whole that the research kept. {root}
- `elements/` holds the full record of every element that the proof of the root rests on, one file each, and \
`elements.md` lists the elements with their files. {elements}
- `references.bib` is the bibliography of the research. The paper cites works that are in it, by their keys, and no \
others.'''
ROOT_FIRST = 'The introduction is written from it: read it in full.'
ROOT_LATER = ('The paper uses the conventions of the root as it is stated in words: read that statement. The rest is '
              'there for when you need more of the whole than the outline in your brief gives.')
ELEMENTS_SECTION = ('Your brief gives an element of another section by what it says. Where that is not enough, for example '
                    'because a proof of this section needs to know how such an element is proved, open its file. '
                    '`plan.json` is the whole plan, for a question about another section that the brief does not answer.')
ELEMENTS_WHOLE = ('`plan.json` says which element each numbered statement states and into which statements the other '
                  'elements are written. Open the records of the elements whose text you change.')

STUDY_FILE = '''- `study.md` is the planning session's account of how the papers it chose for this paper are written, part \
by part, made so that sessions which do not see each other write from one reading of the same papers.'''

WRITE_PROMPT = CONTEXT + '''

This session writes one section of the paper: "{title}", whose id in the plan is `{id}`.{also}

The sections are written by sessions that do not see each other at work. {order} What makes one paper of the sections is \
the plan, which an earlier session made and the script checked. It fixes the numbered statements with their kinds and \
labels, the section of each, what becomes of every other element, and the notation.

In this folder:
''' + METHOD_FILE + '''
''' + BRIEF_FILE.format(tense='is') + ''' Follow the plan as the brief gives it: the same numbered statements with the same \
kinds and labels in the same order, the same treatment of every element, the same notation.
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
one in `parts/`: a repair of that section may remove it.
- Use the notation of the plan for every object that the plan names. An object that the plan does not name is yours to \
name: introduce its notation inside your section, where it is first used, and do not rely on another section having \
introduced it.
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
and labels included, and that TeX typesets the whole. Before \
you finish, read your part from its first line as the reader of the method would, and correct what that reader could not \
follow. Use no source other than the files in this folder.
'''
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
COMPARED_WHOLE = '''A session compared every numbered statement of the manuscript with the statement of its element. \
`findings.json` lists the statements it found to differ. A numbered statement says exactly what its element says \
(method, section "Every numbered statement says what its element says"). Correct each statement that differs, and adjust \
its proof and the places that use it where the correction requires it. When a reported difference is one the method \
permits, keep the statement and say why.'''
LIKE_SECTION = '''A session that had the manuscript and four research articles from refereed journals, and nothing \
else, read the manuscript beside those papers, as the method's section "Reading the manuscript beside real papers" \
describes. `findings.json` holds what it found in this section: places where the manuscript is written otherwise than \
real papers are written. Each finding gives the place ("where"), the passage of the manuscript ("quote", empty when the \
finding is that something is missing), passages from those papers that show what they do at such a place ("evidence"), \
and the difference ("difference").'''
LIKE_WHOLE = '''A session that had the manuscript and four research articles from refereed journals, and nothing \
else, read the manuscript beside those papers, as the method's section "Reading the manuscript beside real papers" \
describes. `findings.json` holds what it found, as far as it concerns no single section: places where the manuscript is \
written otherwise than real papers are written. Each finding gives the place ("where"), the passage of the manuscript \
("quote", empty when the finding is that something is missing), passages from those papers that show what they do at \
such a place ("evidence"), and the difference ("difference").'''
LIKE_KEPT = '''The mathematics stays as it is, and so do the plan and the decisions of the method; the passages show \
manner, and no sentence of theirs is copied or paraphrased into the manuscript. Where following a finding would change \
the mathematics, depart from the plan or undo a decision of the method, such as that the paper names no author or that \
it does not mention Lean, keep the text and say why.'''

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
    'wide': '''TeX typeset the manuscript, and some lines came out wider than the text block, so that they stand out into \
the margin of the printed page. Some displayed formulas may also have less room on their line than they need: TeX then \
closes up the spaces inside the formula, or moves the number of the formula to a line of its own. `findings.json` lists \
these lines and formulas, with the lines of `paper.tex` they come from and by how much each is too wide. Where the line \
is a displayed formula, break the formula over two or more lines, with an environment such as `multline*` or `align*`; a \
formula with a number keeps its number and its label, in `multline` or in `equation` with `split` inside. Where it is a \
line of a paragraph, TeX found no place to break it: display the long formula, or reword the sentence. Change nothing in \
what the text says.''',
    'reading': READ_WHOLE + '''

First compare the understanding with the research: with `root.md`, with the outline of the plan, and with the records \
of the main result and of the elements that its proof names. Where the reader understood something other than what \
these say, the manuscript did not convey it, whether or not a finding points there. Then decide for each finding whether \
the manuscript has to change. A reader can misread, and a finding can ask for something the method excludes; in that case \
keep the text and say why. In every other case revise so that the next reader does not meet the same difficulty, which \
may mean rewriting the passage from the records instead of adjusting its wording.''',
    'comparison': COMPARED_WHOLE,
    'likeness': LIKE_WHOLE + '''

Rewrite the parts so that at each of these places the manuscript does what the papers do: in the structure, the wording, \
the manner and the flow that the passages show, and as the papers in `exemplars/` write. ''' + LIKE_KEPT}

# What a narrow repair is told in the place of the second half, the same for a section and for the whole. It is the
# last repair that its findings receive: no reading of the whole manuscript follows it, only a reading of the passages
# it changed, so it changes the passages that its findings name and nothing else.
NARROW = '''After this repair no session reads the whole manuscript again. The session that reported the findings has read \
every passage of the manuscript as it stands. After the repair another session reads the passages that the repair \
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
NARROW_AGAIN = '''

A finding that carries "open_because" was taken up before and left open, and the text under that key says why: an \
earlier repair kept the text; or its change was found unsound and undone, so that the text is again as it was; or its \
change stayed in the text and was found not to answer the finding; or the finding was repaired and too few readings \
followed to confirm the repair. Decide about such a finding anew, on the text as it stands, with that reason in view.'''
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
    'likeness': LIKE_SECTION + '\n\n' + NARROW_LIKE + LIKE_KEPT + '\n\n' + NARROW}
NARROW_WHOLE_KINDS = {
    'reading': READ_WHOLE + '\n\n' + READ_DECIDE + NARROW_READ + NARROW_TITLE + '\n\n' + NARROW,
    'comparison': COMPARED_WHOLE + '\n\n' + NARROW,
    'likeness': LIKE_WHOLE + '\n\n' + NARROW_LIKE + LIKE_KEPT + NARROW_TITLE + '\n\n' + NARROW}

SECTION_REPAIR_PROMPT = CONTEXT + '''

This session repairs one section of the manuscript that earlier sessions wrote: "{title}", whose id in the plan is \
`{id}`.{also} What was found in a section goes to a session for that section, and these sessions run side by side, so \
this session changes this section and no other.

In this folder:
''' + METHOD_FILE + '''
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
''' + METHOD_FILE + '''
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
- `paper-method.md` is the method the manuscript was written by. Its sections "What of the canon the paper leaves out" and \
"Every numbered statement says what its element says" say what a numbered statement has to say and which differences from \
the record are permitted.
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
statement of an element disagree with each other, say so in "record_disagreement": the Lean statement is the one that \
was proved, and such a disagreement lies in the element's record, which no repair of the manuscript can change.

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
reported is what such a finding asks to be corrected. The array is empty when the only changes are corrections of the \
LaTeX.
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

AGAIN = '''

A session before this one had the same task, and the script could not use what it left, for these reasons:

{problems}

What it left is in `previous-output/`. Do the task again so that these reasons no longer hold.
'''


# ----------------------------------------------------------------------------- the run

def changed_materials(stored, fresh):
    """In what the materials taken from the canon now differ from those a run was started with; empty when in nothing.

    The revision is not compared. It counts the publications of the instance, and a publication that
    changes nothing the proof of the root rests on leaves the paper's materials as they were."""
    fresh = json.loads(json.dumps(fresh))
    found = [f'"{key}"' for key in sorted(set(stored) | set(fresh))
             if key not in ('revision', 'elements') and stored.get(key) != fresh.get(key)]
    old, new = ({element['name']: element for element in materials['elements']} for materials in (stored, fresh))
    for words, names in (('elements that are no longer among them', [name for name in old if name not in new]),
                         ('new elements', [name for name in new if name not in old]),
                         ('elements whose record or standing changed', [name for name in old if name in new and old[name] != new[name]])):
        if names:
            found.append(f'{words}: ' + ', '.join(names[:10]) + (f' and {len(names) - 10} more' if len(names) > 10 else ''))
    if not found and list(old) != list(new):
        found.append('the order of the elements')
    return found


def part_lines(text):
    """The lines of a part as `assemble` puts them into paper.tex."""
    return text.strip('\n').split('\n')


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
    return sum(len(text.encode('utf-8')) for name, text in files.items() if wanted(name))


class Paper:
    """One run of the command: its folder, what it was given, what the sessions made, and the log."""

    def __init__(self, instance, out, tex, choice, parallel=PARALLEL, dry=False):
        self.instance, self.out = Path(instance).resolve(), Path(out).resolve()
        self.settings = load_settings(self.instance)
        first = self.settings['models'][0]
        chosen = {'model': choice.get('model') or first['model'], 'effort': choice.get('effort') or first['effort']}
        # The readings and the comparison come, where the settings name one, from the model that reviews.
        self.writer = chosen
        self.assessor = chosen if choice.get('model') else self.settings['roles'].get('review', self.settings['models'])[0]
        self.recipe = tex_recipe(tex)
        self.parallel, self.dry = max(1, int(parallel)), dry
        # Sessions that run side by side share the log, the numbering of their folders, the parts and the state.
        self.lock = threading.RLock()
        self.stopping, self.running = threading.Event(), set()
        self.log = read_json(self.out / 'log.json') if (self.out / 'log.json').is_file() else []
        numbers = [int(match[0]) for path in (self.out / 'sessions').iterdir() if (match := re.match(r'\d+', path.name))] \
            if (self.out / 'sessions').is_dir() else []
        self.count = max(numbers, default=0)
        self.materials = self.plan = self.layout = self.research = None
        self.parts, self.compared, self.open = {}, {}, []
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

    def event(self, name, **fields):
        with self.lock:
            self.log.append({'event': name, 'at': time.strftime('%Y-%m-%d %H:%M:%S'), **fields})
            if not self.dry:
                write_json(self.out / 'log.json', self.log)

    def save(self):
        """state.json: how far the stages after the writing have come, and what the later ones need of the earlier."""
        with self.lock:
            if not self.dry:
                write_json(self.out / 'state.json', {'done': self.done, 'open': self.open, 'readings': self.readings,
                                                     'rewritten': self.rewritten, 'compared': self.compared,
                                                     'narrow': self.narrow})

    # -- sessions ---------------------------------------------------------------------------------------

    def launch(self, kind, prompt, files, choice, section=None):
        """One session in its own folder: its prompt and its files are written, the CLI runs to its end."""
        with self.lock:
            if self.stopping.is_set():
                raise Stop('the command was interrupted')
            self.count += 1
            folder = self.out / 'sessions' / f"{self.count:02d}-{kind}{'-' + section if section else ''}"
            (folder / 'output').mkdir(parents=True)
        for name, content in files.items():
            (folder / name).parent.mkdir(parents=True, exist_ok=True)
            write_text(folder / name, content)
        write_text(folder / 'prompt.txt', prompt)
        write_json(folder / 'session.json', {'kind': kind, 'section': section, **choice})
        provider = provider_for_model(choice['model'])
        for _ in range(LIMIT_WAITS + 1):
            with WRITING:  # it writes the settings of the session into the folder
                command = worker_command(self.settings['cli'][provider], choice['model'], choice['effort'], folder, {})
            started = time.time()
            try:
                with (folder / 'prompt.txt').open('rb') as inp, (folder / 'cli.stdout.jsonl').open('wb') as out, \
                        (folder / 'cli.stderr.log').open('wb') as err:
                    process = subprocess.Popen(command.argv, cwd=command.cwd, env=worker_environment(), stdin=inp,
                                               stdout=out, stderr=err, shell=False, **popen_options())
                    with self.lock:
                        self.running.add(process)
                    try:
                        code = process.wait()
                    except BaseException:  # the command is interrupted while this thread waits: the session ends with it
                        process.kill()
                        process.wait()
                        raise
                    finally:
                        with self.lock:
                            self.running.discard(process)
            except OSError as exc:
                raise Stop(f'the {kind} session could not be started: {exc}')
            if self.stopping.is_set():
                raise Stop('the command was interrupted')
            limit = detect_usage_limit(provider, folder / 'cli.stdout.jsonl', folder / 'cli.stderr.log', now=time.time(),
                                       fallback_seconds=self.settings['retry_max_seconds'], session_started_at=started)
            self.event('session', folder=folder.relative_to(self.out).as_posix(), kind=kind, section=section, **choice,
                       exit_code=code, seconds=round(time.time() - started, 1),
                       usage_limit_until=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(limit.retry_at)) if limit else None)
            if limit is None:
                break
            # The same session is started again when the limit ends.
            if self.stopping.wait(max(0.0, limit.retry_at - time.time())):
                raise Stop('the command was interrupted')
        return folder

    def session(self, kind, prompt, files, read, choice, section=None, attempts=SESSION_ATTEMPTS):
        """Launch sessions for one task until one leaves output that `read` accepts; returns what `read` returns."""
        problems, previous = None, {}
        for _ in range(attempts):
            text = prompt if problems is None else prompt + AGAIN.format(problems='\n'.join('- ' + p for p in problems))
            folder = self.launch(kind, text, {**files, **previous}, choice, section)
            try:
                return read(folder / 'output')
            except Unusable as exc:
                problems = exc.problems
            except (TypeError, KeyError, AttributeError, UnicodeDecodeError) as exc:
                problems = [f'the output does not have the form the prompt describes ({type(exc).__name__}: {exc})']
            self.event('check', check='output of the ' + kind + ' session', problems=problems)
            previous = {'previous-output/' + path.relative_to(folder / 'output').as_posix():
                        path.read_text(encoding='utf-8', errors='replace')
                        for path in sorted((folder / 'output').rglob('*')) if path.is_file()}
        raise Stop(f'no {kind} session left output the script can use, in {attempts} attempts: ' + '; '.join(problems))

    def side_by_side(self, tasks):
        """Run tasks that do not depend on each other, up to `parallel` at a time; their results, in the order of the tasks.

        Each task keeps on disk what it makes, as soon as it has made it. When one fails for good, the
        tasks that have not begun are not begun, those that are running come to their end and keep
        what they make, and only then is the failure raised, so that a later --resume finds all of it."""
        if len(tasks) < 2 or self.parallel < 2:
            return [task() for task in tasks]
        failed = threading.Event()

        def run(task):
            if failed.is_set() or self.stopping.is_set():
                return None
            try:
                return task()
            except BaseException:
                failed.set()
                raise

        pool = ThreadPoolExecutor(max_workers=min(self.parallel, len(tasks)))
        futures = [pool.submit(run, task) for task in tasks]
        try:
            while wait(futures, timeout=0.5).not_done:  # a wait with an end, so that an interrupt reaches this thread
                pass
        except BaseException:
            # The command is being stopped from outside. The sessions that run end with it, and no other is started.
            self.stopping.set()
            with self.lock:
                for process in list(self.running):
                    process.kill()
            pool.shutdown(wait=True)
            raise
        pool.shutdown()
        for future in futures:
            if future.exception() is not None:
                raise future.exception()
        return [future.result() for future in futures]

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
        return {'paper-method.md': read_file(METHOD), 'user-writing-preferences.md': read_file(PREFERENCES),
                'materials-digest.md': render_digest(self.materials),
                **{name: text for name, text in self.records().items() if name.startswith('elements/')},
                'exemplars.md': render_exemplars(self.collection),
                **{f'exemplars/{key}.tex': text for key, text in self.papers.items()}}

    def kit(self, section):
        """The files of a session that writes or repairs one section: its brief, the records, the account of the
        chosen papers and the papers the plan names for the section."""
        files = {'paper-method.md': read_file(METHOD), 'user-writing-preferences.md': read_file(PREFERENCES),
                 'brief.md': render_brief(self.materials, self.plan, section, self.layout),
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

    @staticmethod
    def load(path, kind=dict):
        if not path.is_file():
            raise Unusable([f'output/{path.name} was not written'])
        try:
            data = json.loads(read_file(path))
        except ValueError as exc:
            raise Unusable([f'output/{path.name} is not JSON: {exc}'])
        if not isinstance(data, kind):
            raise Unusable([f"output/{path.name} holds a JSON {'object' if kind is dict else 'array'}"])
        return data

    # -- stages -----------------------------------------------------------------------------------------

    def take_plan(self, plan, study):
        self.plan, self.study = plan, study
        self.layout = Layout(self.materials, plan)

    def make_plan(self):
        keys = [entry['key'] for entry in self.collection]

        def read(output):
            plan = self.load(output / 'plan.json')
            problems = check_plan(self.materials, plan, keys)
            # The account is passed on as it is; that it exists and is not empty is all the script checks.
            study = read_file(output / 'study.md') if (output / 'study.md').is_file() else ''
            if not study.strip():
                problems.append('output/study.md, the account of how the chosen papers are written, was not written '
                                'or is empty')
            if problems:
                raise Unusable(problems)
            return plan, study

        self.take_plan(*self.session('plan', PLAN_PROMPT, self.planning_kit(), read, self.writer, attempts=PLAN_ATTEMPTS))
        write_text(self.out / 'study.md', self.study)  # the account first: a plan in the folder has its account beside it
        write_json(self.out / 'plan.json', self.plan)
        self.event('plan', statements=len(self.plan['statements']), sections=[s['id'] for s in self.plan['sections']],
                   exemplars=self.plan['exemplars'], papers={s['id']: s['exemplars'] for s in self.plan['sections']},
                   notation=len(self.plan['notation']))

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
            missing = [f'output/{name}.tex was not written or is empty' for name in names
                       if not (output / (name + '.tex')).is_file() or not read_file(output / (name + '.tex')).strip()]
            if missing:
                raise Unusable(missing)
            return {name: read_file(output / (name + '.tex')) for name in names}

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
        tex, spans = assemble(self.plan, self.parts)
        write_text(self.out / 'paper.tex', tex)
        write_text(self.out / 'references.bib', capitals_kept(self.materials['bibliography']))
        elements = {e['name']: e for e in self.materials['elements']}
        by_label = {item['label']: item for item in self.plan['statements']}
        rows = []
        for found in found_statements(self.plan, self.parts):
            if found['label'] not in by_label:
                continue  # the machine check reports it
            element = elements[by_label[found['label']]['element']]
            digest = sha256_text(found['text'])
            judged = self.compared.get(found['label'])
            rows.append({'number': f"{found['kind'].capitalize()} {found['number']}", 'label': found['label'],
                         'element': element['name'], 'states': element['states'] or element['name'],
                         'record_statement': element['statement'], 'record_statement_from': element['statement_from'],
                         'lean_statement': element['lean'], 'paper_statement': found['text'],
                         'paper_statement_sha256': digest,
                         'comparison': ({'verdict': judged['verdict'], 'difference': judged['difference'],
                                         'record_disagreement': judged['record_disagreement']}
                                        if judged and judged['sha256'] == digest else {'verdict': 'not compared'})})
        write_json(self.out / 'correspondence.json', {
            'root': self.materials['root']['name'], 'main_result': self.materials['main'],
            'revision': self.materials['revision'], 'statements': rows, 'others': self.plan['others']})
        return tex, spans, rows

    def settle(self, rounds=REPAIR_ROUNDS):
        """Assemble, check by machine and typeset, with repair sessions for what fails; True when nothing fails.

        `rounds` is the number of repairs at the most. With 0 the manuscript is assembled, checked and
        typeset once, and what fails is reported and not repaired."""
        for round_number in range(rounds + 1):
            tex, spans, _ = self.assemble()
            (self.out / 'paper.pdf').unlink(missing_ok=True)  # a PDF beside the manuscript is always a PDF of it
            found = machine_findings(self.materials, self.plan, self.parts)
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
                    where = [part_at(spans, int(WIDE_LINE.match(problem)[1])) for problem in problems]
                    self.event('check', check=WIDE, problems=problems)
            # What an earlier pass left open about wide lines is replaced by what this pass finds.
            self.open = [item for item in self.open if item['check'] != WIDE]
            if not problems:
                self.save()
                return True
            if round_number < rounds:
                self.repair(kind, problems, where, tex, spans)
        if kind == 'wide':
            # The paper is typeset. A line that still stands out into the margin is reported and stops nothing.
            self.open.append({'check': WIDE, 'after_repairs': rounds, 'problems': problems})
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
        if kind in ('reading', 'comparison', 'likeness'):
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
        answers = kind in ('reading', 'comparison', 'likeness')

        def read(output):
            changed = {name: read_file(output / (name + '.tex')) for name in names
                       if (output / (name + '.tex')).is_file() and read_file(output / (name + '.tex')).strip()}
            changed = {name: text for name, text in changed.items() if text != self.parts[name]}
            response = None
            if answers:
                response = self.load(output / 'response.json', list)
                if len(response) != len(items) or not all(isinstance(r, dict) and r.get('action') in ('revised', 'kept')
                                                          and is_text(r.get('note')) for r in response):
                    raise Unusable([f'output/response.json has one object for each of the {len(items)} findings, with an '
                                    '"action" of "revised" or "kept" and a "note"'])
            if not changed and (not answers or any(r['action'] == 'revised' for r in response)):
                raise Unusable(['no part was changed: write the complete new text of each part you change as '
                                'output/<name>.tex, with the file name it has in parts/'])
            return changed, response

        found = {'understanding': report['understanding'], 'findings': items} if kind == 'reading' else items
        given = {'paper.tex': tex, 'findings.json': json.dumps(found, ensure_ascii=False, indent=2) + '\n',
                 **{f'parts/{name}.tex': self.parts[name] for name in names}}
        lines = '; '.join(f'lines {a} to {b} are `parts/{name}.tex`' for name, a, b in spans if name in names)
        told = ((NARROW_WHOLE_KINDS if section is None else NARROW_SECTION_KINDS)[kind]
                + (NARROW_AGAIN if any('open_because' in item for item in items) else '')) if narrow \
            else (WHOLE_KINDS if section is None else SECTION_KINDS)[kind]
        if section is None:
            papers = {s['id']: self.section_papers(s) for s in sections}
            files = {'paper-method.md': read_file(METHOD), 'user-writing-preferences.md': read_file(PREFERENCES),
                     'plan.json': self.plan_text(), **self.records(), **given}
            if self.collection is not None:
                files['study.md'] = self.study
                files.update({f'exemplars/{key}.tex': self.papers[key] for keys in papers.values() for key in keys})
            prompt = REPAIR_PROMPT.format(
                kind=told, response=RESPONSE if answers else '', spans='Its ' + lines + '.',
                papers=REPAIR_PAPERS.format(papers='; '.join(
                    f"section `{sid}`, " + ' and '.join(f'`exemplars/{key}.tex`' for key in keys)
                    for sid, keys in papers.items())) if self.collection is not None else '',
                **self.research_note())
        else:
            papers = self.section_papers(section)
            files = {**self.kit(section), **given}
            prompt = SECTION_REPAIR_PROMPT.format(
                id=section['id'], title=section['title'], kind=told, response=RESPONSE if answers else '',
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
            report = self.session('read', READ_PROMPT.format(reader=reader), files, read, self.assessor)
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
            report = self.session('likeness', prompt, files, read, self.assessor)
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
        self.open.append({'check': LIKENESS, 'after_repairs': repairs,
                          'problems': [{**departure, 'open_because': ONCE_CONFIRMED} for departure in left]})
        self.save()
        return True

    def compare(self):
        """Every numbered statement against the statement of its element; a repair follows all but the last comparison.

        The statements are compared section by section, the sections side by side: each session has the
        statements of one section and the records of their elements."""
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
            verdicts = [verdict for result in results for verdict in result]
            digests = {row['label']: row['paper_statement_sha256'] for row in rows}
            self.compared = {v['label']: {'verdict': v['verdict'], 'difference': v.get('difference') or '',
                                          'record_disagreement': v['record_disagreement']
                                          if is_text(v.get('record_disagreement')) else '',
                                          'sha256': digests[v['label']]} for v in verdicts}
            self.save()
            differing = [{'label': v['label'], 'difference': v['difference']} for v in verdicts if v['verdict'] == 'differs']
            # A disagreement inside an element's record is reported beside the paper; no repair of the manuscript removes it.
            disagreements = [{'label': label, 'record_disagreement': judged['record_disagreement']}
                             for label, judged in self.compared.items() if judged['record_disagreement']]
            self.event('comparison', round=round_number, differing=differing, record_disagreements=disagreements)
            self.assemble()
            if not differing:
                return True
            if round_number == COMPARISON_ROUNDS:
                self.open.append({'check': COMPARISON, 'after_repairs': COMPARISON_ROUNDS - 1, 'problems': differing})
                self.save()
                return False
            # A repair that changed a part corrected statements and adjusted proofs, so the manuscript is read by
            # itself again before its statements are compared once more; the last thing done is then a comparison.
            self.repair('comparison', differing, [home[item['label']] for item in differing])
            if not self.settle() or not self.read_again():
                return False

    def compare_section(self, section, rows, tex, spans, listed='the numbered statements of this section'):
        """One session that compares the numbered statements of one section; its verdicts, in their order."""
        labels = [row['label'] for row in rows]

        def read(output):
            verdicts = self.load(output / 'comparison.json', list)
            if [v.get('label') if isinstance(v, dict) else None for v in verdicts] != labels \
                    or not all(v.get('verdict') in ('same', 'differs') for v in verdicts) \
                    or not all(is_text(v.get('difference')) for v in verdicts if v['verdict'] == 'differs'):
                raise Unusable(['output/comparison.json has one object for each entry of statements.json, in their order, '
                                'with its "label", a "verdict" of "same" or "differs", and for "differs" the "difference"'])
            return verdicts

        entries = [{key: row[key] for key in ('label', 'number', 'element', 'record_statement', 'lean_statement',
                                              'paper_statement')} for row in rows]
        files = {'paper-method.md': read_file(METHOD), 'paper.tex': tex,
                 'statements.json': json.dumps(entries, ensure_ascii=False, indent=2) + '\n',
                 'records.md': render_records(self.materials, self.plan, {row['element'] for row in rows}, self.layout),
                 **{name: text for name, text in self.records().items() if name.startswith('elements')}}
        lines = next(f'Its lines {a} to {b} are this section.' for name, a, b in spans if name == section['id'])
        return self.session('compare', COMPARE_PROMPT.format(title=section['title'], spans=lines, listed=listed), files,
                            read, self.assessor, section['id'])

    def after_writing(self):
        """The checks, the readings and the comparison of the manuscript, each stage once.

        The manuscript is settled first, in a run that is continued as in a new one, so that paper.tex is
        the parts as they stand. state.json then says which stages are complete; a stage that was begun
        and not ended is made again from its start, which every stage allows, since each works on the
        parts as they stand and is bounded."""
        # A narrow repair that is under way settles the manuscript itself, from the text that was read.
        if False in self.done.values() or (self.narrow is None and not self.settle()):
            return
        for name, method in STAGES:
            if name not in self.done:
                self.done[name] = bool(getattr(self, method)())
                self.save()
            if not self.done[name]:
                return

    def finish(self):
        _, _, rows = self.assemble()
        # A verdict of the comparison holds for the text that was compared. A statement without one for its present
        # text stays open, because nothing after this point compares it: the comparison did not reach it, or a repair
        # changed it afterwards, as a repair of the typesetting under --typeset-only can.
        uncompared = [{'label': row['label'], 'number': row['number']}
                      for row in rows if row['comparison']['verdict'] == 'not compared']
        self.open = [item for item in self.open if item['check'] != UNCOMPARED]
        if uncompared:
            self.open.append({'check': UNCOMPARED, 'after_repairs': 0, 'problems': uncompared})
        self.save()
        status = 'open_findings' if self.open else 'complete' if self.recipe else 'no_tex'
        self.event('end', status=status, open=list(self.open))
        print(f'The manuscript is {self.out / "paper.tex"}; the log is {self.out / "log.json"}.')
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
        shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir(parents=True, exist_ok=True)
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
        return self.session('changes', CHANGES_PROMPT.format(reader=method_part(READER_SECTION)), files, read, self.assessor)

    def narrow_end(self):
        """Leave in the open list, of the findings that the repair took up, those that stay open, each with the reason."""
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
                WIDE: 'the manuscript is typeset again and every line that is too wide goes to repair; this is done '
                      'whenever a finding is acted on, since the typesetting cannot tell these lines from new ones'}
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

        The findings of the readings and of the comparison go to a narrow repair, with the settling and
        the reading of its changes (narrow_run). Then the numbered statements whose text this changed,
        and the chosen ones that were never compared, are compared with their elements, once: a
        statement that differs then is reported as open and is not repaired in the same pass."""
        narrow = self.narrow
        if self.narrow_run():
            before = {name: read_file(self.out / 'narrow' / 'before' / (name + '.tex')) for name in self.parts}
            old = {found['label']: found['text'] for found in found_statements(self.plan, before)}
            tex, spans, rows = self.assemble()
            rows = [row for row in rows if row['comparison']['verdict'] == 'not compared'
                    and (row['label'] in narrow['uncompared'] or old.get(row['label']) != row['paper_statement'])]
            if rows:
                home = {item['label']: item['section'] for item in self.plan['statements']}
                groups = [(section, [row for row in rows if home[row['label']] == section['id']])
                          for section in self.plan['sections']]
                listed = ('those numbered statements of this section whose present text has not been compared with '
                          'their elements, because a repair changed it or because the comparison did not reach it')
                results = self.side_by_side([lambda section=section, stated=stated:
                                             self.compare_section(section, stated, tex, spans, listed)
                                             for section, stated in groups if stated])
                verdicts = [verdict for result in results for verdict in result]
                digests = {row['label']: row['paper_statement_sha256'] for row in rows}
                self.compared.update({v['label']: {'verdict': v['verdict'], 'difference': v.get('difference') or '',
                                                   'record_disagreement': v['record_disagreement']
                                                   if is_text(v.get('record_disagreement')) else '',
                                                   'sha256': digests[v['label']]} for v in verdicts})
                self.save()
                self.event('comparison', round=1 + sum(event['event'] == 'comparison' for event in self.log),
                           statements=[row['label'] for row in rows],
                           differing=[{'label': v['label'], 'difference': v['difference']}
                                      for v in verdicts if v['verdict'] == 'differs'],
                           record_disagreements=[{'label': v['label'], 'record_disagreement': v['record_disagreement']}
                                                 for v in verdicts if is_text(v.get('record_disagreement'))])
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
        self.narrow_end()

    # -- a run that is continued, and a run that is only looked at ----------------------------------------

    def take_up(self):
        """What <out> holds of a run that was stopped: the plan with its account, the parts, the state of the stages."""
        out = self.out
        held = sorted(path.stem for path in (out / 'parts').glob('*.tex')) if (out / 'parts').is_dir() else []
        study = read_file(out / 'study.md') if (out / 'study.md').is_file() else ''
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
        for name in ['abstract'] + [section['id'] for section in sections]:
            path = out / 'parts' / (name + '.tex')
            if path.is_file() and read_file(path).strip():
                self.parts[name] = read_file(path)
        if not self.written(sections[0]):  # the introduction and the abstract are written by one session, or not at all
            for name in ('abstract', sections[0]['id']):
                self.parts.pop(name, None)
        if (out / 'state.json').is_file():
            state = read_json(out / 'state.json')
            self.readings = state['readings']
            # The stages are complete for the parts that were all written. When a section is still to be written,
            # nothing that was read or compared holds for the manuscript that will come of it.
            if all(self.written(section) for section in sections):
                self.done, self.open, self.rewritten, self.compared = (state[key] for key in ('done', 'open', 'rewritten', 'compared'))
                self.narrow = state.get('narrow')

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


def produce(instance, out, tex=None, choice=None, parallel=PARALLEL, resume=False, dry=False):
    """The whole command for a new paper, or with `resume` for one whose run was stopped; returns the exit code.

    With `dry` it makes every check that comes before the first session, launches nothing and writes
    nothing, and prints what the run would do next."""
    out = Path(out)
    if resume:
        if not (out / 'materials.json').is_file():
            raise Stop(f'{out} holds no run of this command to continue: it has no materials.json')
    elif out.exists() and any(out.iterdir()):
        raise Stop(f'{out} is not empty; give a new folder to --out, or --resume to continue the run it holds, or '
                   '--typeset-only to typeset the manuscript it holds')
    model = replay(instance)
    settling_proof(model)  # refuses before anything is written
    if dry:
        # A paper that is missing is fetched by a run, over the network; a dry run names it and fetches nothing.
        manifest, wrong = collection_state()
        papers = {entry['key']: read_file(EXEMPLARS / (entry['key'] + '.tex')) if entry['key'] not in wrong else ''
                  for entry in manifest}
        fetched = None
    else:
        manifest, papers, fetched = load_collection()  # stops, before anything is written, when papers stay missing
    run = Paper(instance, out, tex, choice or {}, parallel, dry)
    run.collection, run.papers = manifest, papers
    materials = extract(instance, model)
    said = ['Dry run: no session is launched and nothing is written.'] if dry else []
    if dry and wrong:
        said.append('Papers of the collection that are missing or differ from its manifest, which a run would fetch: '
                    + ', '.join(wrong) + '.')
    if resume:
        ended = next((event for event in reversed(run.log) if event['event'] == 'end'), None)
        if ended is not None and ended is run.log[-1] and ended['status'] != 'failed':
            raise Stop(f"the run in {out} came to its end ({ended['status']}); there is nothing to continue. "
                       '--typeset-only typesets the manuscript it holds')
        run.materials = read_json(out / 'materials.json')
        differing = changed_materials(run.materials, materials)
        if differing:
            raise Stop(f'what the proof of the root rests on is no longer what {out / "materials.json"} holds, so the canon '
                       'has changed since the run began and it cannot be continued; start a new run in a new folder. '
                       'They differ in ' + '; '.join(differing))
        run.take_up()
        said.append(f"The materials of the canon are those of materials.json: {len(run.materials['elements'])} elements.")
        run.event('resume', plan=run.plan is not None, parts=list(run.parts), done=dict(run.done), parallel=run.parallel)
    else:
        run.materials = materials
        said.append(f"The materials: {len(materials['elements'])} elements that the formal proof of the root rests on.")
        lost = sorted({e['source'] for e in materials['elements'] if e['source']} - set(materials['bibliography_keys']))
        if not dry:
            run.out.mkdir(parents=True, exist_ok=True)
            write_json(run.out / 'materials.json', run.materials)
            write_text(run.out / 'materials.md', render_materials(run.materials))
        run.event('materials', root=run.materials['root']['name'], state=run.materials['root']['state'],
                  settled_by=run.materials['main'], elements=[e['name'] for e in run.materials['elements']],
                  tex=run.recipe[0] if run.recipe else None, parallel=run.parallel,
                  warnings=[f'the source {key} of an element is not in bibliography.bib' for key in lost])
        run.event('collection', folder=str(EXEMPLARS), papers=[entry['key'] for entry in manifest], fetched=fetched)
    if dry:
        print('\n'.join(run.preview(said)))
        return 0
    try:
        if run.narrow is not None and run.narrow.get('pass'):
            run.act()  # the run had come to its end and was stopped while it acted on findings it had left open
        else:
            if run.plan is None:
                run.make_plan()
            run.write_parts()
            run.after_writing()
    except Stop as exc:
        run.event('end', status='failed', error=str(exc))
        raise
    return run.finish()


def act_on_open(instance, out, tex=None, choice=None, parallel=PARALLEL, numbers='all', dry=False):
    """Take up a run that came to its end with findings left open, and act on them; returns the exit code.

    The open findings are those of the last event of the log, which is the `end` of the run. With `dry`
    they are listed with their numbers and nothing else is done. Otherwise those whose numbers
    `numbers` names, or all of them, are acted on as Paper.act describes, and the run ends anew; the
    findings that were not chosen stay open as they were. The run is continued with --resume when it
    is stopped. As for --resume, the canon has to be what the run began with, since the repair
    sessions work from the records."""
    out = Path(out)
    if not all((out / name).is_file() for name in ('materials.json', 'plan.json', 'state.json', 'log.json')):
        raise Stop(f'{out} holds no run of this command that came to its end (materials.json, plan.json, state.json, log.json)')
    run = Paper(instance, out, tex, choice or {}, parallel, dry)
    ended = run.log[-1] if run.log and run.log[-1]['event'] == 'end' and run.log[-1].get('status') != 'failed' else None
    if ended is None:
        raise Stop(f'the run in {out} has not come to its end, so it has no list of open findings to act on: the last '
                   'event of its log.json is not the end of a run. A run that is going comes to its end by itself; '
                   'a run that was stopped is continued with --resume')
    left = json.loads(json.dumps(ended['open']))
    if any(item['check'] in (MACHINE, TYPESETTING) for item in left):
        raise Stop(f'the run in {out} ended before its readings and its comparison were made, because the machine checks '
                   'or the typesetting stayed open; --open-findings acts on what the readings and the comparison of a '
                   'run left open')
    if not left:
        raise Stop(f"the run in {out} came to its end with no finding left open ({ended['status']}); there is nothing "
                   'to act on')
    model = replay(instance)
    settling_proof(model)
    if dry:
        manifest, wrong = collection_state()
        run.collection = manifest
        run.papers = {entry['key']: read_file(EXEMPLARS / (entry['key'] + '.tex')) if entry['key'] not in wrong else ''
                      for entry in manifest}
    else:
        run.collection, run.papers, _ = load_collection()
    run.materials = read_json(out / 'materials.json')
    differing = changed_materials(run.materials, extract(instance, model))
    if differing:
        raise Stop(f'what the proof of the root rests on is no longer what {out / "materials.json"} holds, so the canon '
                   'has changed since the run began, and its open findings cannot be repaired from the records as they '
                   'are now; start a new run in a new folder. They differ in ' + '; '.join(differing))
    run.take_up()
    if run.plan is None or not all(run.written(section) for section in run.plan['sections']):
        raise Stop(f'{out} does not hold the plan and every part of the manuscript whose findings its log lists')
    run.open = left
    listed = run.listed()
    if dry:
        print('\n'.join(run.listing([
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
    try:
        run.act()
    except Stop as exc:
        run.event('end', status='failed', error=str(exc))
        raise
    return run.finish()


def typeset_only(instance, out, tex=None, choice=None, parallel=PARALLEL):
    """Typeset the manuscript a previous run left in `out`, with the same checks and repairs.

    The run that wrote the manuscript has to have carried its reading and its comparison to their end,
    since typesetting does not repeat them, and what that comparison left open stays open. A numbered
    statement that a repair made here changes is not compared again, and `finish` reports it as open."""
    out = Path(out)
    needed = [out / 'materials.json', out / 'plan.json', out / 'parts' / 'abstract.tex']
    if not all(path.is_file() for path in needed):
        raise Stop(f'{out} does not hold a manuscript of this command (materials.json, plan.json, parts/)')
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
    run.materials = read_json(out / 'materials.json')
    run.take_plan(read_json(out / 'plan.json'), read_file(out / 'study.md') if (out / 'study.md').is_file() else '')
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
    run.event('typeset only', tex=run.recipe[0])
    try:
        run.settle()
    except Stop as exc:
        run.event('end', status='failed', error=str(exc))
        raise
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
    parser.add_argument('--tex', nargs=argparse.REMAINDER, help='the TeX command; takes the rest of the command line')
    args = parser.parse_args(argv)
    try:
        options = {'--out', '--model', '--effort', '--typeset-only', '--resume', '--parallel', '--dry-run',
                   '--open-findings'}
        if args.tex is not None and (not args.tex or options & set(args.tex)):
            raise Stop('--tex takes the rest of the command line: name a command after it, and put it last')
        if args.parallel < 1:
            raise Stop('--parallel is the number of sessions that run side by side, at least 1')
        if args.typeset_only and (args.resume or args.dry_run):
            raise Stop('--typeset-only typesets a finished manuscript; it goes with neither --resume nor --dry-run')
        if args.open_findings is not None and (args.typeset_only or args.resume):
            raise Stop('--open-findings takes up a run that came to its end; it goes with neither --typeset-only nor '
                       '--resume. A pass over open findings that was stopped is continued with --resume alone')
        choice = {'model': args.model, 'effort': args.effort}
        if args.open_findings is not None:
            return act_on_open(args.instance, args.out, args.tex, choice, args.parallel, args.open_findings, args.dry_run)
        if args.typeset_only:
            return typeset_only(args.instance, args.out, args.tex, choice, args.parallel)
        return produce(args.instance, args.out, args.tex, choice, args.parallel, args.resume, args.dry_run)
    except (Stop, OSError, ValueError) as exc:
        print('paper.py: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    contain_session_processes()  # whatever a session starts ends with this command
    raise SystemExit(main())
