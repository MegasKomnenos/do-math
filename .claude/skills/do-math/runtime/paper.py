"""Write the paper of an instance whose root is settled by a formal proof.

    python paper.py <instance> --out <folder> [--model <provider/model>] [--effort <effort>]
                    [--typeset-only] [--tex <command...>]

One command produces the paper to the end without stopping for the user. What the sessions it
launches do not decide is fixed in ../reference/paper-method.md, which they receive. The stages:

  materials    everything the formal proof of the root rests on is taken from the canon
  plan         a session decides how each element appears in the paper; the script checks the plan
  write        one session per section writes its LaTeX, in the order of the paper
  settle       the script assembles paper.tex, checks it by machine and typesets it; what fails
               goes to a repair session, and the manuscript is assembled and checked again
  reading      a session that has only the manuscript reads it as the paper's reader, and a repair
               session takes up what it found
  comparison   a session compares every numbered statement with the statement of its element

Every loop is bounded by the constants below. Sessions run one at a time, each in its own folder
under <out>/sessions with its prompt and the files it is given, and the script reads the files the
prompt asked for. <out> receives paper.tex, references.bib, paper.pdf, plan.json,
correspondence.json (which element each numbered statement states; never inside the paper),
materials.md and log.json (what was launched and what each check found). The work stays beside
them: materials.json, parts/ (the abstract and the sections as they stand), sessions/ and typeset/.

--tex takes the rest of the command line, so it comes last. It names tectonic, latexmk or pdflatex,
which are run in the way each needs, or any other command, which is run once in the folder of the
manuscript with `paper.tex` appended and has to leave paper.pdf. Without --tex the first of the
three found on PATH is used. When there is none, everything except the typesetting is done and the
command says so; --typeset-only later typesets the manuscript that <out> already holds.

Exit codes: 0 the paper is complete; 1 refused or failed; 2 produced with findings left open
(log.json names them); 3 the manuscript is complete and no TeX command was available.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

from canon import BIB_ENTRY, Canon, declaration_text, read_record, sha256_text, split_review
from cli_adapter import detect_usage_limit, provider_for_model
from knowledge import ROOT_QUESTION, replay
from launch import worker_command, worker_environment
from runtime_support import contain_session_processes, popen_options, read_json, write_json, write_text
from settings import load_settings

REFERENCE = Path(__file__).resolve().parents[1] / 'reference'
METHOD = REFERENCE / 'paper-method.md'
PREFERENCES = REFERENCE / 'user-writing-preferences.md'
READER_SECTION = 'The reader'  # the part of the method that the reading session receives, and nothing else of it

PLAN_ATTEMPTS = 3      # planning sessions before the command gives up on a plan it can carry out
SESSION_ATTEMPTS = 2   # sessions of any other kind before it gives up on output it can read
REPAIR_ROUNDS = 3      # repair sessions for one round of machine checks and typesetting
READING_ROUNDS = 2     # independent readings, each followed by a repair of what it found
COMPARISON_ROUNDS = 2  # comparisons of the statements; a repair follows every one but the last
LIMIT_WAITS = 12       # times one session is started again after the account's usage limit
TEX_SECONDS = 600      # one TeX command

ENGINES = ('tectonic', 'latexmk', 'pdflatex')
NUMBERED = ('theorem', 'proposition', 'lemma', 'corollary', 'definition')
ENVIRONMENT = re.compile(r'\\begin\{(' + '|'.join(NUMBERED) + r')\}(.*?)\\end\{\1\}', re.S)
VERIFICATION = re.compile(r'\\begin\{verification\}(.*?)\\end\{verification\}', re.S)
FORBIDDEN = re.compile(r'\\(documentclass|usepackage|newcommand|renewcommand|providecommand|def|newtheorem|section|'
                       r'bibliography|bibliographystyle|maketitle|title|author|input|include|setcounter|numberwithin|'
                       r'newenvironment|renewenvironment|DeclareMathOperator|let)\b')
CITE = re.compile(r'\\cite(?:\[[^\]]*\])?\{([^}]*)\}')
REF = re.compile(r'\\(?:eq|page)?ref\{([^}]*)\}')
LABEL = re.compile(r'\\label\{([^}]*)\}')
SECTION_ID = re.compile(r'[a-z][a-z0-9-]*')
LABEL_FORM = re.compile(r'[a-z]+:[a-z0-9-]+')

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
\newtheorem*{verification}{Formal verification}
\numberwithin{equation}{section}
'''
TEX_SPECIAL = {'\\': r'\textbackslash{}', '{': r'\{', '}': r'\}', '$': r'\$', '&': r'\&', '#': r'\#', '%': r'\%',
               '_': r'\_', '^': r'\^{}', '~': r'\~{}'}
LEAN_SYMBOLS = {
    '→': r'\to', '←': r'\leftarrow', '↔': r'\leftrightarrow', '↦': r'\mapsto', '↑': r'\uparrow', '∀': r'\forall',
    '∃': r'\exists', '¬': r'\neg', '∧': r'\wedge', '∨': r'\vee', '≤': r'\le', '≥': r'\ge', '≠': r'\ne', '≡': r'\equiv',
    '≃': r'\simeq', '∈': r'\in', '∉': r'\notin', '⊆': r'\subseteq', '⊂': r'\subset', '∩': r'\cap', '∪': r'\cup',
    '∖': r'\setminus', '∅': r'\emptyset', '×': r'\times', '∘': r'\circ', '·': r'\cdot', '∑': r'\sum', '∏': r'\prod',
    '∫': r'\int', '∂': r'\partial', '√': r'\surd', '∞': r'\infty', '⊤': r'\top', '⊥': r'\bot', '⊔': r'\sqcup',
    '⊓': r'\sqcap', '∣': r'\mid', '‖': r'\|', '⌊': r'\lfloor', '⌋': r'\rfloor', '⌈': r'\lceil', '⌉': r'\rceil',
    '⟨': r'\langle', '⟩': r'\rangle', '«': r'\ll', '»': r'\gg', '⁻': '^{-}',
    'ℕ': r'\mathbb{N}', 'ℤ': r'\mathbb{Z}', 'ℚ': r'\mathbb{Q}', 'ℝ': r'\mathbb{R}', 'ℂ': r'\mathbb{C}',
    'Γ': r'\Gamma', 'Δ': r'\Delta', 'Θ': r'\Theta', 'Λ': r'\Lambda', 'Ξ': r'\Xi', 'Π': r'\Pi', 'Σ': r'\Sigma',
    'Φ': r'\Phi', 'Ψ': r'\Psi', 'Ω': r'\Omega'}
for _number, _name in enumerate('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi o pi rho '
                                'varsigma sigma tau upsilon phi chi psi omega'.split()):
    LEAN_SYMBOLS[chr(0x3B1 + _number)] = _name if _name == 'o' else '\\' + _name
for _digit in range(10):
    LEAN_SYMBOLS[chr(0x2080 + _digit)] = '_{%d}' % _digit
    LEAN_SYMBOLS['⁰¹²³⁴⁵⁶⁷⁸⁹'[_digit]] = '^{%d}' % _digit


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
        if not statement:
            text = (canon.lean / index[name]['file']).read_text(encoding='utf-8').replace('\r\n', '\n')
            item['definition_text'] = declaration_text(text, index[name]['span'])
        return item

    question = canon.questions / (ROOT_QUESTION + '.md')
    bibliography = read_file(canon.bibliography) if canon.bibliography.is_file() else ''
    root = model['root']
    root_sections = sections_of(root)
    return {'revision': model['sequence'], 'root': {
                'name': root, 'state': model['root_state'], 'words': read_file(instance / 'root.md').strip(),
                'lean': elements[root]['statement'], 'statement': root_sections.get('Statement'),
                'explanation': root_sections.get('Explanation')},
            'main': main, 'axioms': elements[main]['axioms'], 'allowed_axioms': model['allowed_axioms'],
            'understanding': split_review(read_file(question))[0].strip() if question.is_file() else '',
            'elements': [entry(name) for name in order],
            'bibliography': bibliography, 'bibliography_keys': BIB_ENTRY.findall(bibliography),
            'identifiers': sorted(set(elements) | {e['module'] for e in elements.values()})}


def render_materials(materials):
    """The materials as one text for a session to read from beginning to end."""
    root = materials['root']
    proved = root['state'] == 'formal_proved'
    names = lambda values: ', '.join('`' + v + '`' for v in values) or '(nothing)'
    lines = ['# Materials for the paper', '',
             f"Taken by script from the canon at revision {materials['revision']}. A name between backquotes, such as "
             f"`{root['name']}`, is the name of a Lean declaration. It identifies an element here and in the plan, "
             'and it does not appear in the paper.', '',
             '## The root', '', 'The root in words, as it was fixed when the research began:', '',
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
              materials['understanding'] or 'No account of the problem as a whole has been written.', '',
              '## The elements the proof rests on', '',
              f"{len(materials['elements'])} elements in dependence order: each comes after everything its statement "
              'mentions and its proof names, and the last is the main result.', '']
    for number, element in enumerate(materials['elements'], 1):
        lines += [f"### {number}. `{element['name']}`", '',
                  f"{element['kind']} · weight: {element['weight']}"
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
            lines.append(f"Its statement mentions {names(element['mentions'])}. Its proof names {names(element['uses'])}.")
        else:
            lines.append(f"It is defined from {names(sorted(set(element['mentions'] + element['uses'])))}.")
        lines += ([f"Among these elements it is named or mentioned by {names(element['used_by'])}."]
                  if element['used_by'] else []) + ['']
        for title, key in (('Description', 'description'), ('Statement', 'statement'), ('Explanation', 'explanation'),
                           ('Proof', 'proof'), ('Literature', 'literature')):
            if element[key]:
                note = (f" (from the record of `{element['statement_from']}`)"
                        if key == 'statement' and element['statement_from'] != element['name'] else '')
                lines += [f'**{title}{note}.**', '', element[key], '']
    lines += ['## Bibliography', '']
    lines += ['```bibtex', materials['bibliography'].strip(), '```'] if materials['bibliography'].strip() else \
        ['The canon has no bibliography: the paper cites nothing.']
    return '\n'.join(lines) + '\n'


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


def check_plan(materials, plan):
    """The reasons the script cannot carry a plan out, as sentences for the next planning session."""
    problems = []
    bad = problems.append
    elements = {e['name']: e for e in materials['elements']}
    if not isinstance(plan, dict):
        return ['plan.json holds one JSON object']
    for key in ('title', 'outline'):
        if not is_text(plan.get(key)):
            bad(f'"{key}" is a nonempty text')
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
    order = {section.get('id'): number for number, section in enumerate(sections)}
    if len(order) != len(sections):
        bad('two sections have the same id')
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
    return problems


def assignment(materials, plan, section):
    """What the plan puts into one section, as lines for the session that writes it."""
    elements = {e['name']: e for e in materials['elements']}
    by_element = {item['element']: item for item in plan['statements']}
    sid, lines = section['id'], []

    def proof_of(item):
        return item.get('proof', item['section']) if elements[item['element']]['kind'] == 'statement' else None

    def called(item):
        return f"{item['kind']} `{item['label']}`"

    for item in plan['statements']:
        proof = proof_of(item)
        if item['section'] == sid:
            tail = ('' if proof is None else '; it is cited and not proved' if proof == 'cited'
                    else '; its proof follows it' if proof == sid else f'; its proof is written in section `{proof}`')
            lines.append(f"- stated here: {called(item)}, which states the element `{item['element']}`{tail}")
        elif proof == sid:
            lines.append(f"- proved here: {called(item)} (`{item['element']}`), stated in section `{item['section']}`")
    for item in plan['others']:
        if item['treatment'] == 'cited' and item['section'] == sid:
            lines.append(f"- cited in the running text: `{item['element']}`")
        for target in item.get('into', []) if item['treatment'] == 'absorbed' else []:
            if target == sid:
                lines.append(f"- written into the running text: `{item['element']}`")
            elif target in by_element and sid in (by_element[target]['section'], proof_of(by_element[target])):
                lines.append(f"- absorbed into {called(by_element[target])}: `{item['element']}`")
    lines = lines or ['- the plan places no element in this section']
    for item in plan['others']:
        if item['treatment'] == 'not_stated':
            lines.append(f"- stated nowhere in the paper: `{item['element']}`; `{item['by']}` stands in its place")
    return '\n'.join(lines)


# ----------------------------------------------------------------------------- the manuscript

def lean_tex(text):
    """A Lean statement in typewriter type; a symbol outside ASCII becomes its mathematical symbol.

    Returns the LaTeX and the characters for which the table has no symbol."""
    lines, unknown = [], []
    for line in text.split('\n'):
        body = line.lstrip(' ')
        piece = '~' * (len(line) - len(body))
        for char in body:
            if char in TEX_SPECIAL:
                piece += TEX_SPECIAL[char]
            elif ord(char) < 128:
                piece += char
            elif char in LEAN_SYMBOLS:
                piece += r'\ensuremath{' + LEAN_SYMBOLS[char] + '}'
            else:
                unknown.append(char)
                piece += r'\ensuremath{\langle\mathrm{U{+}%04X}\rangle}' % ord(char)
        lines.append(piece)
    return '\\\\\n'.join(lines), sorted(set(unknown))


def main_element(materials):
    return next(e for e in materials['elements'] if e['main'])


def uncommented(text):
    return re.sub(r'(?<!\\)%.*', '', text)


def assemble(materials, plan, parts):
    """paper.tex from the parts, in the order of the plan, and the lines each part occupies in it."""
    cites = any(CITE.search(uncommented(text)) for text in parts.values())
    lines = (PREAMBLE + '\\newcommand{\\LeanStatement}{\\begin{quote}\\ttfamily\\raggedright\ntheorem '
             + lean_tex(main_element(materials)['lean'])[0] + '\n\\end{quote}}\n\\begin{document}\n\\title{'
             + plan['title'].strip() + '}\n\\begin{abstract}').split('\n')
    spans = []

    def add(name):
        body = parts[name].strip('\n').split('\n')
        spans.append((name, len(lines) + 1, len(lines) + len(body)))
        lines.extend(body)

    add('abstract')
    lines += ['\\end{abstract}', '\\maketitle']
    for section in plan['sections']:
        lines += ['', '\\section{' + section['title'].strip() + '}\\label{sec:' + section['id'] + '}']
        add(section['id'])
    if cites:
        lines += ['', '\\bibliographystyle{amsplain}', '\\bibliography{references}']
    lines += ['\\end{document}', '']
    return '\n'.join(lines), spans


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


def machine_checks(materials, plan, parts):
    """What a machine can check in the manuscript, as sentences for a repair session; empty when all hold."""
    problems = []
    bad = problems.append
    elements = {e['name']: e for e in materials['elements']}
    first = plan['sections'][0]['id']
    texts = {'the title': plan['title'], 'abstract': parts['abstract'], **{s['id']: parts[s['id']] for s in plan['sections']}}
    # Every numbered statement is one the plan names, of the planned kind, in the planned section and order.
    found = found_statements(plan, parts)
    planned = [(item['label'], item['kind'], item['section']) for item in plan['statements']]
    got = [(item['label'], item['kind'], item['section']) for item in found]
    for label, kind, section in planned:
        if (label, kind, section) not in got:
            bad(f'part {section}: the plan has a {kind} with \\label{{{label}}} here, and the part has none')
    for item in found:
        if (item['label'], item['kind'], item['section']) not in planned:
            bad(f"part {item['section']}: the {item['kind']} numbered {item['number']} "
                + (f"with \\label{{{item['label']}}}" if item['label'] else 'without a \\label')
                + ' is not a numbered statement of the plan; every numbered statement states an element the plan names')
    # A statement without a \label has the label None, which cannot be ordered beside a text; repr can.
    if sorted(got, key=repr) == sorted(planned, key=repr) and got != planned:
        bad('the numbered statements are not in the order of the plan: ' + ', '.join(label for label, _, _ in planned))
    by_label = {item['label']: item for item in found}
    for item in plan['statements']:
        # A statement is followed by its proof, or proved in the section the plan names, or cited and not proved.
        element, label, here = elements[item['element']], item['label'], by_label.get(item['label'])
        proof = item.get('proof', item['section']) if element['kind'] == 'statement' else None
        if here is None or proof is None:
            continue
        if proof == 'cited':
            if element['source'] not in [k.strip() for m in CITE.finditer(here['text']) for k in m[1].split(',')]:
                bad(f"part {item['section']}: {label} is a result from the literature; its statement carries "
                    f"\\cite{{{element['source']}}}")
            if here['proof_follows']:
                bad(f"part {item['section']}: {label} is a result from the literature; it is cited and has no proof")
        elif proof == item['section']:
            if not here['proof_follows']:
                bad(f"part {proof}: the proof of {label} follows its statement directly, in a proof environment")
        elif not re.search(r'\\begin\{proof\}\[[^\]]*\\ref\{' + re.escape(label) + r'\}', uncommented(parts[proof])):
            bad(f"part {proof}: the plan puts the proof of {label} here; it opens with \\begin{{proof}}[Proof of ...~\\ref{{{label}}}]")
    for item in plan['others']:
        key = elements[item['element']]['source']
        if item['treatment'] == 'cited' and key not in [k.strip() for m in CITE.finditer(uncommented(parts[item['section']]))
                                                        for k in m[1].split(',')]:
            bad(f"part {item['section']}: the plan cites the result with the bibliography key {key} here, and the part does not")
    # The formal verification is reported in one remark of the introduction, around the statement the script supplies.
    remarks = {name: VERIFICATION.findall(uncommented(text)) for name, text in texts.items()}
    total = sum(uncommented(text).count('\\LeanStatement') for text in texts.values())
    if [name for name, hits in remarks.items() for _ in hits] != [first] or total != 1 \
            or remarks[first][0].count('\\LeanStatement') != 1:
        bad(f'part {first}: the introduction has exactly one verification environment, and \\LeanStatement stands '
            'once in it and nowhere else')
    # Labels and citations resolve.
    labels = ['sec:' + s['id'] for s in plan['sections']] + [m[1] for text in texts.values() for m in LABEL.finditer(uncommented(text))]
    for label in sorted({label for label in labels if labels.count(label) > 1}):
        bad(f'\\label{{{label}}} is defined more than once')
    keys = set(materials['bibliography_keys'])
    for name, text in texts.items():
        plain = uncommented(text)
        for target in sorted({m[1] for m in REF.finditer(plain)} - set(labels)):
            bad(f'{name}: \\ref{{{target}}} points to a label that the manuscript does not define')
        for key in sorted({k.strip() for m in CITE.finditer(plain) for k in m[1].split(',')} - keys):
            bad(f'{name}: \\cite{{{key}}} is not a key of the bibliography; only works in the bibliography of the materials are cited')
        commands = sorted({m[1] for m in FORBIDDEN.finditer(plain)})
        if commands and name != 'the title':
            bad(f'{name}: a part does not use ' + ', '.join('\\' + c for c in commands) + '; the script supplies the preamble, '
                'the title, the section headings and the bibliography')
        strange = sorted({c for c in text if ord(c) > 127})
        if strange:
            bad(f'{name}: the manuscript is written in ASCII; write these characters as LaTeX: ' + ' '.join(strange))
    if REF.search(uncommented(parts['abstract'])) or CITE.search(uncommented(parts['abstract'])):
        bad('abstract: the abstract stands by itself, without \\ref and without \\cite')
    # No Lean name of the canon outside the verification remark, comments and labels included.
    pattern = identifier_pattern(materials['identifiers'])
    for name, text in texts.items():
        names = sorted({m[0] for m in pattern.finditer(VERIFICATION.sub('', text).replace('\\_', '_'))})
        if names:
            bad(f'{name}: Lean names of the canon appear outside the verification remark: ' + ', '.join(names))
    return problems


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


# ----------------------------------------------------------------------------- prompts

CONTEXT = '''A script is turning a finished piece of mathematical research into a paper. The research is a Lean library, \
called the canon, whose main statement, the root, has been settled by a formal proof; every declaration of the library is \
an element, and beside it is a written record. The script launches AI sessions one after another, and each does one part \
of the work. No session can ask another what it meant, and nobody answers questions while the script runs.'''

FILES = '''- `paper-method.md` is the method that every session follows. It fixes who the paper is for, what each of its \
parts does, which elements become numbered statements, the order, what of the canon the paper leaves out, and the manner of \
writing. Read it in full before anything else. Its decisions are made; your work applies them to this research.
- `materials.md` holds everything the proof of the root rests on: the root in words and in Lean, the account of the problem \
as a whole, each element with its record, in dependence order, and the bibliography. It is the only source of the \
mathematics and of the literature. Read it in full.
- `user-writing-preferences.md` describes the writing that the person who will read the paper first prefers, with the \
occasions on which the preferences came to light. The method says how it bears on a paper.'''

PLAN_PROMPT = CONTEXT + '''

This session plans the paper. The sessions after it write the sections from the plan, and the script holds the manuscript \
to it.

In this folder:
''' + FILES + '''

Write one file, `output/plan.json`: a JSON object with the keys below. A value that will be printed (the title, a section \
title, a symbol) is LaTeX; inside a JSON string a backslash is written twice.

- "title": the title of the paper.
- "outline": a few sentences for the writers saying how the proof goes and at which step its difficulty lies. The outline \
of the proof in the introduction, and the room each proof receives, follow it.
- "sections": the sections in the order of the paper, each {"id", "title", "content"}. "id" is a short lowercase word \
([a-z][a-z0-9-]*) that names the section in file names and labels. "content" says in a sentence or two what the section \
does and what it contains. The first section is the introduction. The abstract and the list of references are not sections.
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
- "notation": the symbols of the paper for the objects of the materials, each {"symbol", "meaning"}. The writers use \
these and no others for the same objects.

The script accepts the plan when every element of the materials appears in it exactly once; when kinds, labels, sections \
and reasons have the form above; when the main result is a theorem stated in the first section before every other \
theorem, proposition, lemma and corollary; when no statement mentions an object that is defined in a later numbered \
definition, and no proof comes before a numbered statement it rests on; when an element absorbed into a numbered \
statement is one that statement or its proof rests on; when only results with a source in the literature are cited; and \
when an element that is not stated has in its place an element its proof names, another proof of the same statement, or \
the definition it is stated to agree with. A plan that fails goes to a new planning session with the list of failures.

Use no source other than the files in this folder. Write no part of the paper itself.
'''

WRITE_PROMPT = CONTEXT + '''

This session writes one section of the paper: "{title}", whose id in the plan is `{id}`.{also}

In this folder:
''' + FILES + '''
- `plan.json` is the plan of the paper, made by an earlier session and checked by the script. Follow it: the same \
numbered statements with the same kinds and labels in the same order, the same treatment of every element, the same \
notation. Its "outline" says how the proof goes and where its difficulty lies.
- `parts/` holds what has been written so far, as the paper will carry it{parts}. Your section continues it in the same \
notation and the same voice, and does not repeat it.

What the plan gives this section: {content}

{assignment}

Write `output/{id}.tex`: the body of the section in LaTeX, beginning after the section heading, which the script \
supplies.{abstract} The method's section "The LaTeX of a part" says what the script supplies and what a part contains.

The script checks afterwards that the numbered statements of your part are those of the plan, that every \\ref and \\cite \
resolves, that no Lean name of the canon appears outside the verification remark, and that TeX typesets the whole. Before \
you finish, read your part from its first line as the reader of the method would, and correct what that reader could not \
follow. Use no source other than the files in this folder.
'''

REPAIR_KINDS = {
    'machine': '''The script's checks of the assembled manuscript found the problems listed in `findings.json`. Each is a \
requirement of the method or of the plan. Correct every one.''',
    'typeset': '''TeX could not typeset the manuscript. `findings.json` holds the errors of the TeX run; line numbers in \
them are lines of `paper.tex`. Correct the cause of each error in the part where it lies.''',
    'reading': '''A session that had the manuscript and nothing else read it as the reader the method describes. \
`findings.json` holds its report: "understanding" is what that reader took the paper to prove and how; "findings" are the \
places where the reader could not follow, missed something, found an error, or met text that does not belong in a paper.

First compare the understanding with the materials. Where the reader understood something other than what the materials \
say, the manuscript did not convey it, whether or not a finding points there. Then decide for each finding whether the \
manuscript has to change. A reader can misread, and a finding can ask for something the method excludes; in that case keep \
the text and say why. In every other case revise so that the next reader does not meet the same difficulty, which may \
mean rewriting the passage from the materials instead of adjusting its wording.''',
    'comparison': '''A session compared every numbered statement of the manuscript with the statement of its element. \
`findings.json` lists the statements it found to differ. A numbered statement says exactly what its element says \
(method, section "Every numbered statement says what its element says"). Correct each statement that differs, and adjust \
its proof and the places that use it where the correction requires it. When a reported difference is one the method \
permits, keep the statement and say why.'''}

REPAIR_PROMPT = CONTEXT + '''

This session repairs the manuscript that earlier sessions wrote.

In this folder:
''' + FILES + '''
- `plan.json` is the plan of the paper. A repair keeps it: the same numbered statements, kinds, labels and order.
- `parts/` holds the parts of the manuscript as they stand: `abstract.tex` and one file per section.
- `paper.tex` is the manuscript the script assembled from them. {spans}
- `findings.json` holds what was found.

{kind}

For every part you change, write its complete new text as `output/<name>.tex`, with the file name it has in `parts/`. \
Leave unchanged parts out.{response} The script then assembles the manuscript again and repeats its checks. Use no source \
other than the files in this folder.
'''
RESPONSE = ''' Write also `output/response.json`: an array with one object for each entry of the findings, in their \
order, {"finding": <its number, from 1>, "action": "revised" or "kept", "note": "<what you changed, or why the text stays>"}.'''

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
- "findings": an array, empty when you have none. Each is {{"where": "...", "quote": "...", "problem": "..."}}: the \
section or the numbered statement, the exact words of the manuscript, and what is wrong or missing there together with \
what you would have needed. Report every place where you could not follow a step of an argument; where a term or a \
symbol is used before it is defined, or is never defined; where a reference points to something that is absent or comes \
later; where a proof does not prove what its statement says, or has a gap or an error; where the notation or the wording \
of one thing changes; and where the text does not belong in a mathematical paper, for example because it speaks of how \
the paper or its proofs were produced.
'''

COMPARE_PROMPT = CONTEXT + '''

This session compares the numbered statements of the manuscript with the statements they come from. The paper is of use \
only if each of its numbered statements says exactly what was proved.

In this folder:
- `paper-method.md` is the method the manuscript was written by. Its sections "What of the canon the paper leaves out" and \
"Every numbered statement says what its element says" say what a numbered statement has to say and which differences from \
the record are permitted.
- `materials.md` holds the elements with their records.
- `paper.tex` is the manuscript, for the definitions and the notation in which its statements are read.
- `statements.json` lists the numbered statements: for each its label, its number, the element it states, the statement \
of that element in words as its record gives it, the element's Lean statement, and the statement as the manuscript has it.

For each entry decide whether the statement of the manuscript says exactly what the statement of the element says: the \
same objects, the same hypotheses, the same quantifiers and ranges, the same conclusion, neither stronger nor weaker, \
read with the definitions and the notation of the manuscript. A difference the method permits is no difference as long \
as the mathematical content is the same. Where a convention changed, for example an index that now starts at one, check \
that the statement was carried over correctly, case by case at the boundary. Where the statement in words and the Lean \
statement of an element disagree with each other, say so in "record_disagreement": the Lean statement is the one that \
was proved, and such a disagreement lies in the element's record, which no repair of the manuscript can change.

Write `output/comparison.json`: an array with one object for each entry, {"label": "...", "verdict": "same" or \
"differs", "difference": "<what differs, exactly; empty when the verdict is same>", "record_disagreement": "<where the \
statement in words and the Lean statement of the element disagree, exactly; empty when they agree>"}. Use no source \
other than the files in this folder.
'''

AGAIN = '''

A session before this one had the same task, and the script could not use what it left, for these reasons:

{problems}

What it left is in `previous-output/`. Do the task again so that these reasons no longer hold.
'''


# ----------------------------------------------------------------------------- the run

class Paper:
    """One run of the command: its folder, what it was given, what the sessions made, and the log."""

    def __init__(self, instance, out, tex, choice):
        self.instance, self.out = Path(instance).resolve(), Path(out).resolve()
        self.settings = load_settings(self.instance)
        first = self.settings['models'][0]
        chosen = {'model': choice.get('model') or first['model'], 'effort': choice.get('effort') or first['effort']}
        # The reading and the comparison come, where the settings name one, from the model that reviews.
        self.writer = chosen
        self.assessor = chosen if choice.get('model') else self.settings['roles'].get('review', self.settings['models'])[0]
        self.recipe = tex_recipe(tex)
        self.log = read_json(self.out / 'log.json') if (self.out / 'log.json').is_file() else []
        self.count = len(list((self.out / 'sessions').iterdir())) if (self.out / 'sessions').is_dir() else 0
        self.materials = self.plan = None
        self.parts, self.compared, self.open = {}, {}, []

    def event(self, name, **fields):
        self.log.append({'event': name, 'at': time.strftime('%Y-%m-%d %H:%M:%S'), **fields})
        write_json(self.out / 'log.json', self.log)

    # -- sessions ---------------------------------------------------------------------------------------

    def launch(self, kind, prompt, files, choice, section=None):
        """One session in its own folder: its prompt and its files are written, the CLI runs to its end."""
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
            command = worker_command(self.settings['cli'][provider], choice['model'], choice['effort'], folder, {})
            started = time.time()
            try:
                with (folder / 'prompt.txt').open('rb') as inp, (folder / 'cli.stdout.jsonl').open('wb') as out, \
                        (folder / 'cli.stderr.log').open('wb') as err:
                    code = subprocess.run(command.argv, cwd=command.cwd, env=worker_environment(), stdin=inp,
                                          stdout=out, stderr=err, shell=False, **popen_options()).returncode
            except OSError as exc:
                raise Stop(f'the {kind} session could not be started: {exc}')
            limit = detect_usage_limit(provider, folder / 'cli.stdout.jsonl', folder / 'cli.stderr.log', now=time.time(),
                                       fallback_seconds=self.settings['retry_max_seconds'], session_started_at=started)
            self.event('session', folder=folder.relative_to(self.out).as_posix(), kind=kind, section=section, **choice,
                       exit_code=code, seconds=round(time.time() - started, 1),
                       usage_limit_until=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(limit.retry_at)) if limit else None)
            if limit is None:
                break
            time.sleep(max(0.0, limit.retry_at - time.time()))  # the same session is started again when the limit ends
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

    def given(self, *more):
        """The files every writing session receives, with those of its task."""
        files = {'paper-method.md': read_file(METHOD), 'user-writing-preferences.md': read_file(PREFERENCES),
                 'materials.md': render_materials(self.materials)}
        if 'plan' in more:
            files['plan.json'] = json.dumps(self.plan, ensure_ascii=False, indent=2) + '\n'
        if 'parts' in more:
            files.update({f'parts/{name}.tex': text for name, text in self.parts.items()})
        return files

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

    def make_plan(self):
        def read(output):
            plan = self.load(output / 'plan.json')
            problems = check_plan(self.materials, plan)
            if problems:
                raise Unusable(problems)
            return plan

        self.plan = self.session('plan', PLAN_PROMPT, self.given(), read, self.writer, attempts=PLAN_ATTEMPTS)
        write_json(self.out / 'plan.json', self.plan)
        self.event('plan', statements=len(self.plan['statements']), sections=[s['id'] for s in self.plan['sections']])

    def write_parts(self):
        for number, section in enumerate(self.plan['sections']):
            names = [section['id']] + (['abstract'] if number == 0 else [])

            def read(output):
                missing = [f'output/{name}.tex was not written or is empty' for name in names
                           if not (output / (name + '.tex')).is_file() or not read_file(output / (name + '.tex')).strip()]
                if missing:
                    raise Unusable(missing)
                return {name: read_file(output / (name + '.tex')) for name in names}

            prompt = WRITE_PROMPT.format(
                id=section['id'], title=section['title'], content=section['content'],
                assignment=assignment(self.materials, self.plan, section),
                also=' As the first section it is the introduction, and this session also writes the abstract.' if number == 0 else '',
                parts='' if number else '; it is empty, because this is the first section',
                abstract=(' Write also `output/abstract.tex`: the text of the abstract, without the abstract environment. '
                          'The introduction carries the remark on formal verification that the method describes.') if number == 0 else '')
            self.keep(self.session('write', prompt, self.given('plan', 'parts'), read, self.writer, section['id']))

    def keep(self, parts):
        self.parts.update(parts)
        for name, text in parts.items():
            (self.out / 'parts').mkdir(exist_ok=True)
            write_text(self.out / 'parts' / (name + '.tex'), text)

    def assemble(self):
        """paper.tex, references.bib and the correspondence file from the parts as they stand."""
        tex, spans = assemble(self.materials, self.plan, self.parts)
        write_text(self.out / 'paper.tex', tex)
        write_text(self.out / 'references.bib', self.materials['bibliography'])
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

    def settle(self):
        """Assemble, check by machine and typeset, with a repair session for what fails; True when nothing fails."""
        for round_number in range(REPAIR_ROUNDS + 1):
            tex, spans, _ = self.assemble()
            (self.out / 'paper.pdf').unlink(missing_ok=True)  # a PDF beside the manuscript is always a PDF of it
            kind, problems = 'machine', machine_checks(self.materials, self.plan, self.parts)
            self.event('check', check='machine checks of the manuscript', problems=problems)
            if not problems and self.recipe:
                folder = self.out / 'typeset'
                folder.mkdir(exist_ok=True)
                for name in ('paper.tex', 'references.bib'):
                    shutil.copyfile(self.out / name, folder / name)
                kind, problems = 'typeset', typeset(folder, self.recipe)
                self.event('check', check='typesetting', command=self.recipe[0], problems=problems)
                if not problems:
                    shutil.copyfile(folder / 'paper.pdf', self.out / 'paper.pdf')
            if not problems:
                return True
            if round_number < REPAIR_ROUNDS:
                self.repair(kind, problems, tex, spans)
        self.open.append({'check': 'typesetting' if kind == 'typeset' else 'machine checks of the manuscript',
                          'after_repairs': REPAIR_ROUNDS, 'problems': problems})
        return False

    def repair(self, kind, findings, tex=None, spans=None):
        """A session that changes the parts for what a check or a reader found."""
        if tex is None:
            tex, spans, _ = self.assemble()
        answers = kind in ('reading', 'comparison')
        count = len(findings['findings']) if kind == 'reading' else len(findings)

        def read(output):
            changed = {name: read_file(output / (name + '.tex')) for name in self.parts
                       if (output / (name + '.tex')).is_file() and read_file(output / (name + '.tex')).strip()}
            changed = {name: text for name, text in changed.items() if text != self.parts[name]}
            response = None
            if answers:
                response = self.load(output / 'response.json', list)
                if len(response) != count or not all(isinstance(r, dict) and r.get('action') in ('revised', 'kept')
                                                     and is_text(r.get('note')) for r in response):
                    raise Unusable([f'output/response.json has one object for each of the {count} findings, with an '
                                    '"action" of "revised" or "kept" and a "note"'])
            if not changed and (not answers or any(r['action'] == 'revised' for r in response)):
                raise Unusable(['no part was changed: write the complete new text of each part you change as '
                                'output/<name>.tex, with the file name it has in parts/'])
            return changed, response

        files = {**self.given('plan', 'parts'), 'paper.tex': tex,
                 'findings.json': json.dumps(findings, ensure_ascii=False, indent=2) + '\n'}
        prompt = REPAIR_PROMPT.format(
            kind=REPAIR_KINDS[kind], response=RESPONSE if answers else '',
            spans='Its ' + '; '.join(f'lines {a} to {b} are `parts/{name}.tex`' for name, a, b in spans) + '.')
        changed, response = self.session('repair', prompt, files, read, self.writer, kind)
        self.keep(changed)
        self.event('repair', of=kind, changed=sorted(changed), response=response)

    def read_and_repair(self):
        """Independent readings of the manuscript, each followed by a repair of what the reader found."""
        reader = method_part(READER_SECTION)

        def read(output):
            report = self.load(output / 'reading.json')
            findings = report.get('findings')
            if not report.get('understanding') or not isinstance(findings, list) \
                    or not all(isinstance(f, dict) and is_text(f.get('where')) and is_text(f.get('problem')) for f in findings):
                raise Unusable(['output/reading.json has "understanding" and "findings", an array whose entries have a '
                                '"where" and a "problem"'])
            return report

        for round_number in range(1, READING_ROUNDS + 1):
            files = {'paper.tex': read_file(self.out / 'paper.tex'), 'references.bib': self.materials['bibliography']}
            report = self.session('read', READ_PROMPT.format(reader=reader), files, read, self.assessor)
            self.event('reading', round=round_number, understanding=report['understanding'], findings=report['findings'])
            if not report['findings']:
                return True
            self.repair('reading', {'understanding': report['understanding'], 'findings': report['findings']})
            if not self.settle():
                return False
        self.event('note', text=f'The manuscript was read {READING_ROUNDS} times, and each reading had findings. What '
                                'the last repair changed has not been read again.')
        return True

    def compare(self):
        """Every numbered statement against the statement of its element; a repair follows all but the last comparison."""
        for round_number in range(1, COMPARISON_ROUNDS + 1):
            _, _, rows = self.assemble()
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
            files = {'paper-method.md': read_file(METHOD), 'materials.md': render_materials(self.materials),
                     'paper.tex': read_file(self.out / 'paper.tex'),
                     'statements.json': json.dumps(entries, ensure_ascii=False, indent=2) + '\n'}
            verdicts = self.session('compare', COMPARE_PROMPT, files, read, self.assessor)
            digests = {row['label']: row['paper_statement_sha256'] for row in rows}
            self.compared = {v['label']: {'verdict': v['verdict'], 'difference': v.get('difference') or '',
                                          'record_disagreement': v['record_disagreement']
                                          if is_text(v.get('record_disagreement')) else '',
                                          'sha256': digests[v['label']]} for v in verdicts}
            differing = [{'label': v['label'], 'difference': v['difference']} for v in verdicts if v['verdict'] == 'differs']
            # A disagreement inside an element's record is reported beside the paper; no repair of the manuscript removes it.
            disagreements = [{'label': label, 'record_disagreement': judged['record_disagreement']}
                             for label, judged in self.compared.items() if judged['record_disagreement']]
            self.event('comparison', round=round_number, differing=differing, record_disagreements=disagreements)
            self.assemble()
            if not differing:
                return True
            if round_number == COMPARISON_ROUNDS:
                self.open.append({'check': 'comparison of the numbered statements with their elements',
                                  'after_repairs': COMPARISON_ROUNDS - 1, 'problems': differing})
                return False
            self.repair('comparison', differing)
            if not self.settle():
                return False

    def finish(self):
        self.assemble()
        status = 'open_findings' if self.open else 'complete' if self.recipe else 'no_tex'
        self.event('end', status=status, open=self.open)
        print(f'The manuscript is {self.out / "paper.tex"}; the log is {self.out / "log.json"}.')
        if self.open:
            print('Findings are left open after the bounded repairs:')
            for item in self.open:
                print(f"- {item['check']}: {len(item['problems'])} left; log.json has them")
        if not self.recipe:
            print('No TeX command was available (none of ' + ', '.join(ENGINES) + ' is on PATH, and --tex was not given), '
                  'so paper.pdf was not typeset. Everything else is done. When a TeX command is available, run this '
                  'command again with --typeset-only and the same --out.')
        elif not self.open:
            print(f'The paper is {self.out / "paper.pdf"}.')
        return {'complete': 0, 'open_findings': 2, 'no_tex': 3}[status]


def produce(instance, out, tex=None, choice=None):
    """The whole command for a new paper; returns the exit code."""
    out = Path(out)
    if out.exists() and any(out.iterdir()):
        raise Stop(f'{out} is not empty; give a new folder to --out, or --typeset-only to typeset the manuscript it holds')
    model = replay(instance)
    settling_proof(model)  # refuses before anything is written
    run = Paper(instance, out, tex, choice or {})
    run.out.mkdir(parents=True, exist_ok=True)
    run.materials = extract(instance, model)
    write_json(run.out / 'materials.json', run.materials)
    write_text(run.out / 'materials.md', render_materials(run.materials))
    unknown = lean_tex(main_element(run.materials)['lean'])[1]
    lost = sorted({e['source'] for e in run.materials['elements'] if e['source']} - set(run.materials['bibliography_keys']))
    run.event('materials', root=run.materials['root']['name'], state=run.materials['root']['state'],
              settled_by=run.materials['main'], elements=[e['name'] for e in run.materials['elements']],
              tex=run.recipe[0] if run.recipe else None,
              warnings=([f'the formal statement has characters without a LaTeX form: {" ".join(unknown)}'] if unknown else [])
              + [f'the source {key} of an element is not in bibliography.bib' for key in lost])
    try:
        run.make_plan()
        run.write_parts()
        if run.settle() and run.read_and_repair():
            run.compare()
    except Stop as exc:
        run.event('end', status='failed', error=str(exc))
        raise
    return run.finish()


def typeset_only(instance, out, tex=None, choice=None):
    """Typeset the manuscript a previous run left in `out`, with the same checks and repairs.

    The run that wrote the manuscript has to have carried its reading and its comparison to their end,
    since typesetting does not repeat them, and what that comparison left open stays open."""
    out = Path(out)
    needed = [out / 'materials.json', out / 'plan.json', out / 'parts' / 'abstract.tex']
    if not all(path.is_file() for path in needed):
        raise Stop(f'{out} does not hold a manuscript of this command (materials.json, plan.json, parts/)')
    run = Paper(instance, out, tex, choice or {})
    if run.recipe is None:
        raise Stop('no TeX command is available: none of ' + ', '.join(ENGINES) + ' is on PATH, and --tex was not given')
    # The first end in the log is that of the run that wrote the manuscript. The machine checks and the
    # typesetting are made again here, and nothing else is.
    produced = next((event for event in run.log if event['event'] == 'end'), {})
    left = produced.get('open', [])
    if produced.get('status') not in ('complete', 'no_tex', 'open_findings') \
            or any(item['check'] in ('machine checks of the manuscript', 'typesetting') for item in left):
        raise Stop(f'{out} holds a manuscript whose reading and comparison did not run to their end; --typeset-only '
                   'typesets only a manuscript that an earlier run finished apart from the typesetting')
    run.open = list(left)
    run.materials, run.plan = read_json(out / 'materials.json'), read_json(out / 'plan.json')
    run.parts = {name: read_file(out / 'parts' / (name + '.tex')) for name in ['abstract'] + [s['id'] for s in run.plan['sections']]}
    if (out / 'correspondence.json').is_file():
        run.compared = {row['label']: {**row['comparison'], 'sha256': row['paper_statement_sha256']}
                        for row in read_json(out / 'correspondence.json')['statements']
                        if row['comparison']['verdict'] != 'not compared'}
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
    parser.add_argument('--out', type=Path, required=True, help='the folder that receives the paper; new or empty')
    parser.add_argument('--model', help='<provider>/<model> for every session, the reading and the comparison included; '
                                        'default: the first of the instance\'s models for planning, writing and repair, '
                                        'and the first model of the review role for the reading and the comparison')
    parser.add_argument('--effort', help='the effort of planning, writing and repair, and of every session when --model '
                                         'is given; default: that of the instance\'s first model, and, for the reading '
                                         'and the comparison without --model, that of the review role\'s first model')
    parser.add_argument('--typeset-only', action='store_true', help='typeset the manuscript that --out already holds')
    parser.add_argument('--tex', nargs=argparse.REMAINDER, help='the TeX command; takes the rest of the command line')
    args = parser.parse_args(argv)
    try:
        if args.tex is not None and (not args.tex or {'--out', '--model', '--effort', '--typeset-only'} & set(args.tex)):
            raise Stop('--tex takes the rest of the command line: name a command after it, and put it last')
        choice = {'model': args.model, 'effort': args.effort}
        return (typeset_only if args.typeset_only else produce)(args.instance, args.out, args.tex, choice)
    except (Stop, OSError, ValueError) as exc:
        print('paper.py: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    contain_session_processes()  # whatever a session starts ends with this command
    raise SystemExit(main())
