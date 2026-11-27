"""The canon of an instance: one Lean library with a written record beside each declaration.

An element is a declaration of that library together with its record. This module holds what
every part of the runtime needs to know about the canon's files: where a record lives, how a
record, an approach entry and a candidate change are written, how a candidate is applied to
the library, and how the structural index is extracted from the compiled library by Lean.
It judges no mathematics. For the formats as a session uses them, see ../reference/records.md for the written texts,
../reference/change-format.md for a candidate change and ../reference/canon.md for the Lean files.

Layout under <instance>/canon/:
    lean/                  the module root of the library; every module is a `module` file
    records/<Name>.md      one record per declaration, at a path that follows its name
    approaches/<Name>/     the approaches tried on an element whose proof is not accepted
    questions/<id>.md      the understanding so far of a question
    evidence/<Name>/       files a record refers to (computations, data)
    history/<Name>/        what a replacement left behind: the difference and where it went
    bibliography.bib       the sources of every result taken from the literature
    index.json             the structural index, extracted by machine at each publication
"""
import difflib
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil

from runtime_support import alive, first_commit, git, read_json, remove_file, replace_file, write_text

EXTRACT_MODULE = 'DoMathExtract'
ROW_MARK = '@@canon '
WEIGHTS = ('unit', 'step')
RECORD_KEYS = ('short', 'weight', 'proves', 'refutes', 'source')
RECORD_SECTIONS = ('Description', 'Statement', 'Explanation', 'Proof', 'Literature')
APPROACH_KEYS = ('title', 'sessions')
APPROACH_SECTIONS = ('Idea', 'Established', 'Where it stops')
REVIEW_SECTION = 'Review'  # written by the runner from review's assessment, never by a session
STATEMENT_KINDS = ('theorem',)
ENTRY_KINDS = ('theorem', 'def', 'opaque', 'axiom', 'inductive')
WINDOWS_RESERVED = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}
IMPORT_LINE = re.compile(r'^(?:public\s+)?(?:meta\s+)?import\s+(all\s+)?(\S+)')  # group 1: `all`, when it is there; group 2: the module


class CanonError(ValueError):
    """A candidate or a canon file that the runtime cannot carry; the message says what to correct."""


class Canon:
    """The paths of one instance's canon."""

    def __init__(self, instance):
        self.instance = Path(instance).resolve()
        self.root = self.instance / 'canon'
        self.lean = self.root / 'lean'
        self.records = self.root / 'records'
        self.approaches = self.root / 'approaches'
        self.questions = self.root / 'questions'
        self.evidence = self.root / 'evidence'
        self.history = self.root / 'history'
        self.bibliography = self.root / 'bibliography.bib'
        self.index = self.root / 'index.json'

    def load_index(self):
        return read_index(self.index) if self.index.exists() else empty_index()


def empty_index():
    return {'revision': 0, 'modules': {}, 'entries': {}, 'aux': {}, 'hidden': {}, 'pairs': {}}


def read_index(path):
    """An index file in the form this code writes, whichever version of the code wrote the file.

    An entry carries under `axioms` what `Lean.collectAxioms` gave for its declaration when its module
    was last extracted. An index written before the extraction asked Lean for the axioms carries
    instead, under `direct_axioms`, the axioms each entry reaches without passing through another
    entry, and the axioms of an entry were then those of everything it uses, added up from these lists.
    Such an index is read with that sum made once, here, so that an instance created by the earlier code
    stands as it stood. Nothing is written back. The index file takes the present form at the next
    publication that changes a Lean source, and an entry's list is Lean's own from the time its module
    is next extracted. The earlier index also kept, under `judged`, which proofs a separate program had
    checked; that is no longer kept."""
    index = read_json(path)
    entries = index['entries']
    if not any('direct_axioms' in entry for entry in entries.values()):
        return index
    axioms = {name: set(entry['direct_axioms']) | ({name} if entry['kind'] == 'axiom' else set())
              for name, entry in entries.items()}
    users = {}
    for name, entry in entries.items():
        for used in entry['uses'] + entry['statement_uses']:
            if used in entries:
                users.setdefault(used, []).append(name)
    pending = list(entries)
    while pending:
        name = pending.pop()
        for user in users.get(name, ()):
            if not axioms[name] <= axioms[user]:
                axioms[user] |= axioms[name]
                pending.append(user)
    return {'revision': index['revision'], 'modules': index['modules'],
            'entries': {name: {**{key: value for key, value in entry.items() if key != 'direct_axioms'},
                               'axioms': sorted(axioms[name])} for name, entry in entries.items()},
            'aux': index['aux'],
            'hidden': {name: {**{key: value for key, value in item.items() if key != 'axioms'},
                              'sorry': 'sorryAx' in item['axioms']}
                       for name, item in index.get('hidden', {}).items()},
            'pairs': index.get('pairs', {})}


# ----------------------------------------------------------------------------- names and paths

def name_parts(name):
    """The components of a Lean name; a component written between « and » may contain dots."""
    parts, current, quoted = [], '', False
    for char in name:
        if char == '«':
            quoted = True
        elif char == '»':
            quoted = False
        elif char == '.' and not quoted:
            parts.append(current)
            current = ''
        else:
            current += char
    parts.append(current)
    if not all(parts):
        raise CanonError(f'not a declaration name: {name!r}')
    return parts


def path_part(part):
    """One name component as a file name that Windows accepts and that maps back unambiguously."""
    safe = ''.join(c if c not in '<>:"/\\|?*%' and ord(c) >= 32 else '%{:02X}'.format(ord(c)) for c in part)
    if safe.upper() in WINDOWS_RESERVED or safe.endswith(('.', ' ')):
        safe += '%'
    return safe


def name_path(name):
    """The relative path that follows a declaration name: `A.B.c` is `A/B/c`."""
    return '/'.join(path_part(p) for p in name_parts(name))


def record_file(canon, name):
    return canon.records / (name_path(name) + '.md')


def sha256_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


# Files in a peer's or an organizer's output folder that are no part of the candidate: the receipt that
# `prepare` writes about the other files, and the session's end decision, which its host moves out of the
# folder when the turn ends (ending.py). A receipt that counted the decision would stop matching the
# candidate at that moment, and a finished candidate would be made again by another peer.
PREPARED = 'prepared.json'
BESIDE_CANDIDATE = (PREPARED, 'end-decision.json')


def tree_hash(root, skip=()):
    """One identity for a folder's files, by relative path and content."""
    digest = hashlib.sha256()
    root = Path(root)
    for path in sorted(p for p in root.rglob('*') if p.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative in skip:
            continue
        digest.update(relative.encode('utf-8') + b'\0' + hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


# ----------------------------------------------------------------------------- written files

def parse_sectioned(text, keys, sections, what, review=False):
    """A file with a `key: value` header between two `---` lines and `## Section` parts.

    Every top-level heading must be one of the named sections, at most once each, so that the
    traversal command can return a part by itself. Deeper headings are free. With review, the
    runner's own Review section is accepted and returned under its name."""
    lines = text.replace('\r\n', '\n').split('\n')
    if not lines or lines[0].strip() != '---':
        raise CanonError(f'{what}: the file begins with a line "---" and a header of "key: value" lines')
    meta, index = {}, 1
    while index < len(lines) and lines[index].strip() != '---':
        line = lines[index]
        index += 1
        if not line.strip():
            continue
        key, separator, value = line.partition(':')
        key = key.strip()
        if not separator or key not in keys:
            raise CanonError(f'{what}: unknown header line {line!r}; the keys are {", ".join(keys)}')
        if key in meta:
            raise CanonError(f'{what}: header key {key} appears twice')
        meta[key] = value.strip()
    if index >= len(lines):
        raise CanonError(f'{what}: the header is not closed by a line "---"')
    allowed = sections + ((REVIEW_SECTION,) if review else ())
    parts, current = {}, None
    fenced = False
    for line in lines[index + 1:]:
        if line.lstrip().startswith('```'):
            fenced = not fenced
        if line.startswith('## ') and not fenced:
            title = line[3:].strip()
            if title not in allowed:
                raise CanonError(f'{what}: unknown section "## {title}"; the sections are {", ".join(sections)}')
            if title in parts:
                raise CanonError(f'{what}: section "## {title}" appears twice')
            current = title
            parts[current] = []
            continue
        if current is None:
            if line.strip():
                raise CanonError(f'{what}: text before the first section; begin with "## {sections[0]}"')
            continue
        parts[current].append(line)
    return {'meta': meta, 'sections': {name: '\n'.join(body).strip() for name, body in parts.items()}}


def parse_record(text, what='record'):
    record = parse_sectioned(text, RECORD_KEYS, RECORD_SECTIONS, what)
    meta, sections = record['meta'], record['sections']
    if meta.get('weight') not in WEIGHTS:
        raise CanonError(f'{what}: the header needs "weight: unit" or "weight: step"')
    if not sections.get('Description'):
        raise CanonError(f'{what}: the record needs a nonempty "## Description"')
    for key in ('proves', 'refutes'):
        if key in meta:
            try:
                name_parts(meta[key])
            except CanonError as error:
                raise CanonError(f'{what}: header key {key}: {error}') from None
    if 'proves' in meta and 'refutes' in meta:
        raise CanonError(f'{what}: a declaration is another proof of a statement or a refutation of one, not both')
    return record


def parse_approach(text, what='approach'):
    entry = parse_sectioned(text, APPROACH_KEYS, APPROACH_SECTIONS, what, review=True)
    if not entry['meta'].get('title'):
        raise CanonError(f'{what}: the header needs a "title"')
    for name in ('Idea', 'Where it stops'):
        if not entry['sections'].get(name):
            raise CanonError(f'{what}: the entry needs a nonempty "## {name}"')
    entry['meta']['sessions'] = [s.strip() for s in entry['meta'].get('sessions', '').split(',') if s.strip()]
    return entry


REVIEW_HEADING = re.compile(r'^## ' + REVIEW_SECTION + r'[ \t]*$', re.MULTILINE)


def split_review(text):
    """A text and the Review section the runner appended to it, which a session never writes."""
    text = text.replace('\r\n', '\n')
    found = REVIEW_HEADING.search(text)
    if not found:
        return text.rstrip() + '\n', None
    return text[:found.start()].rstrip() + '\n', text[found.end():].strip()


def with_review(text, review):
    body, _ = split_review(text)
    return body if not review else body + '\n## ' + REVIEW_SECTION + '\n\n' + review.strip() + '\n'


def read_question_account(canon, question):
    """Read the published account together with its review, including the publication stamp."""
    path = canon.questions / (question + '.md')
    return split_review(path.read_text(encoding='utf-8-sig')) if path.is_file() else ('', None)


# ----------------------------------------------------------------------------- Lean sources

# One item of a Lean header: `module`, `prelude`, or an import with its modifiers and its module.
HEADER_ITEM = re.compile(r'(?:module|prelude)(?=\s|$)|(?:public\s+)?(?:meta\s+)?import\s+(?:all\s+)?\S+')


def header_code(lines):
    """The code of a Lean file with its comments left out: (index of the line, code), one item of a header at a time.

    Ordinary and nested comments are skipped, and a comment inside a line separates what stands on its two
    sides, as it does for Lean. Lean reads a header word by word and not line by line, so one line can hold
    several of its items, as in `import A import B`. Each item is given by itself, and what follows the last
    item of a line as one more piece. Every reader of a header reads through this, so that the commands, the
    runner and the Lean broker take the same items for the header of one file; a reader stops at the first
    piece that is no item of a header."""
    depth = 0
    for number, line in enumerate(lines):
        code, index = [], 0
        while index < len(line):
            if depth:
                if line.startswith('/-', index):
                    depth, index = depth + 1, index + 2
                elif line.startswith('-/', index):
                    depth, index = depth - 1, index + 2
                else:
                    index += 1
            elif line.startswith('--', index):
                break
            elif line.startswith('/-', index):
                code.append(' ')
                depth, index = 1, index + 2
            else:
                code.append(line[index])
                index += 1
        rest = ''.join(code).strip()
        while rest:
            found = HEADER_ITEM.match(rest)
            piece = found[0] if found else rest
            yield number, piece
            rest = rest[len(piece):].lstrip()


def header_scan(lines):
    """The index after the last import line of a Lean file's header, whether it is a `module` file, and its imports."""
    last, module, imports = 0, False, []
    for number, stripped in header_code(lines):
        if stripped == 'module':
            module, last = True, number + 1
        elif stripped == 'prelude':
            last = number + 1
        elif found := IMPORT_LINE.match(stripped):
            last = number + 1
            imports.append(found[2])
        else:
            break
    return last, module, imports


def add_imports(text, imports):
    """The source with `public import` lines for the named modules added to its header."""
    lines = text.split('\n')
    end, module, present = header_scan(lines)
    wanted = [name for name in dict.fromkeys(imports) if name not in present]
    new = [('public import ' if module else 'import ') + name for name in wanted]
    return '\n'.join(lines[:end] + new + lines[end:])


def declaration_text(text, span):
    """The source text of a declaration; span is [first line, column, last line, column], lines from 1."""
    lines = text.split('\n')
    first, start, last, end = span
    if first == last:
        return lines[first - 1][start:end]
    return '\n'.join([lines[first - 1][start:], *lines[first:last - 1], lines[last - 1][:end]])


def replace_span(text, span, replacement):
    lines = text.split('\n')
    first, start, last, end = span
    merged = lines[first - 1][:start] + replacement.strip('\n') + lines[last - 1][end:]
    return '\n'.join(lines[:first - 1] + merged.split('\n') + lines[last:])


def module_file(module):
    return '/'.join(module.split('.')) + '.lean'


def library_modules(lean_root, library):
    """Every module of the library under a module root, as (module name, path), in name order."""
    lean_root = Path(lean_root)
    found = []
    for path in list((lean_root / library).rglob('*.lean')) + [lean_root / (library + '.lean')]:
        if path.is_file():
            found.append(('.'.join(path.relative_to(lean_root).with_suffix('').parts), path))
    return sorted(found)


def with_importers(lean_root, library, modules):
    """The named modules and every module of the library that imports one of them, directly or through others.

    Lean elaborates a declaration in the environment its module imports. A module whose own source did
    not change can therefore come out different when a module it imports gained an import: an instance
    or a notation that is now in scope can alter what an unchanged statement says. The index of such a
    module is extracted again with the modules that changed, so that the checks of a change see it."""
    needs = {name: set(header_scan(path.read_text(encoding='utf-8').replace('\r\n', '\n').split('\n'))[2])
             for name, path in library_modules(lean_root, library)}
    reached, pending = set(modules), list(modules)
    while pending:
        current = pending.pop()
        for name, imported in needs.items():
            if current in imported and name not in reached:
                reached.add(name)
                pending.append(name)
    return sorted(reached)


# ----------------------------------------------------------------------------- candidates

CHANGE_KEYS = {'title', 'description', 'replace', 'questions', 'resolutions', 'retire'}


def load_change(candidate):
    """A candidate's manifest, with the files its folders hold, checked for structure only.

    A candidate mirrors the canon: lean/ holds new modules, records/ new or replacing records,
    approaches/ entries, questions/ replacing understanding texts, evidence/ files, and
    bibliography.bib entries to add. change.json names what cannot be read from the layout:
    which existing declarations get a new proof, and the questions proposed or resolved."""
    candidate = Path(candidate)
    data = read_json(candidate / 'change.json')
    if not isinstance(data, dict):
        raise CanonError('change.json is an object')
    unknown = sorted(set(data) - CHANGE_KEYS)
    if unknown:
        raise CanonError('unknown key in change.json: ' + ', '.join(unknown))
    for key in ('title', 'description'):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise CanonError(f'change.json needs a nonempty "{key}"')
    replace = data.setdefault('replace', [])
    if not isinstance(replace, list):
        raise CanonError('change.json "replace" is an array')
    seen = set()
    for item in replace:
        if not isinstance(item, dict) or set(item) - {'declaration', 'file', 'imports'}:
            raise CanonError('a replacement has "declaration", "file" and optionally "imports"')
        name = item.get('declaration')
        if not isinstance(name, str) or name in seen:
            raise CanonError(f'missing or repeated replacement declaration: {name!r}')
        seen.add(name)
        name_parts(name)
        relative_file(candidate, item.get('file'))
        imports = item.setdefault('imports', [])
        if not isinstance(imports, list) or not all(isinstance(i, str) and i for i in imports):
            raise CanonError('"imports" lists module names')
    for key in ('questions', 'resolutions', 'retire'):
        if not isinstance(data.setdefault(key, []), list):
            raise CanonError(f'change.json "{key}" is an array')
    for item in data['retire']:
        if not isinstance(item, dict) or set(item) != {'alternative', 'into', 'reason'}:
            raise CanonError('a retirement has "alternative", "into" and "reason"')
        if not all(isinstance(value, str) and value.strip() for value in item.values()):
            raise CanonError('"alternative", "into" and "reason" of a retirement are nonempty text')
    files = lambda folder, suffix: sorted(p.relative_to(candidate / folder).as_posix()
                                          for p in (candidate / folder).rglob('*' + suffix) if p.is_file())
    data['modules'] = files('lean', '.lean')
    data['records'] = files('records', '.md')
    data['approaches'] = files('approaches', '.md')
    data['understanding'] = files('questions', '.md')
    for relative in data['records']:
        parse_record((candidate / 'records' / relative).read_text(encoding='utf-8-sig'), 'records/' + relative)
    for relative in data['approaches']:
        text = (candidate / 'approaches' / relative).read_text(encoding='utf-8-sig')
        entry = parse_approach(text, 'approaches/' + relative)
        # A line `## Review` inside a code block is no section of the entry, and publication still cuts the entry
        # at that line (with_review), so it is refused here like the section.
        if REVIEW_SECTION in entry['sections'] or split_review(text)[1] is not None:
            raise CanonError(f'approaches/{relative}: the "## {REVIEW_SECTION}" section is written at publication, from review')
    for relative in data['understanding']:
        text = (candidate / 'questions' / relative).read_text(encoding='utf-8-sig')
        if not text.strip():
            raise CanonError(f'questions/{relative} is empty')
        if split_review(text)[1] is not None:
            raise CanonError(f'questions/{relative}: the "## {REVIEW_SECTION}" section is written at publication, from review')
    return data


def relative_file(root, name):
    if not isinstance(name, str) or not name.strip():
        raise CanonError('a file reference is a nonempty relative path')
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or any(c in name for c in ('\\', ':', '\0')):
        raise CanonError('file must be a relative /-separated path: ' + name)
    actual = (Path(root) / name).resolve()
    if not actual.is_relative_to(Path(root).resolve()) or not actual.is_file():
        raise CanonError('missing or escaping file: ' + name)
    return actual


PLAIN_COMPONENT = re.compile(r"[^\W\d][\w'!?]*")


def path_name(path):
    """The declaration name a record path follows; the inverse of name_path.

    A component that is not a plain identifier is written between « and », as Lean prints it."""
    parts = []
    for part in PurePosixPath(path).parts:
        if part.endswith('%'):
            part = part[:-1]
        part = re.sub(r'%([0-9A-F]{2})', lambda m: chr(int(m[1], 16)), part)
        parts.append(part if PLAIN_COMPONENT.fullmatch(part) else '«' + part + '»')
    return '.'.join(parts)


def case_collisions(names):
    """Groups of names whose records would be one file where the file system ignores case."""
    groups = {}
    for name in names:
        groups.setdefault(name_path(name).casefold(), []).append(name)
    return sorted(tuple(sorted(group)) for group in groups.values() if len(group) > 1)


def apply_rearrangement(lean_root, candidate, delete):
    """An organizer's rearrangement: complete module files under rewrite/lean/ and modules to delete.

    Only the organizer rewrites existing files, and what it may change is checked afterwards from the
    index: every element keeps its name and statement. Returns the modules written and those removed."""
    lean_root, source = Path(lean_root), Path(candidate) / 'rewrite/lean'
    written = []
    if source.is_dir():
        for path in sorted(p for p in source.rglob('*.lean') if p.is_file()):
            relative = path.relative_to(source)
            target = lean_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            written.append('.'.join(relative.with_suffix('').parts))
    removed = []
    for module in delete:
        target = lean_root / module_file(module)
        if target.is_file():
            target.unlink()
            removed.append(module)
    return written, removed


def apply_lean(lean_root, candidate, change, index, bases=None, library=None):
    """Apply a candidate's Lean part to a module root: add its modules, replace the named declarations.

    A new module never replaces a file. A replacement puts the candidate's complete declaration text
    where the declaration stands now, found through the index, and adds the imports it names. bases
    maps a replaced declaration to the identity of the text the candidate was prepared against; when
    the canon holds another text now, another publication replaced that proof in between, and
    applying this one would silently discard it. Returns the modules whose source changed."""
    lean_root, candidate = Path(lean_root), Path(candidate)
    bases = bases or {}
    changed = []
    for relative in change['modules']:
        target = lean_root / relative
        if library and PurePosixPath(relative).with_suffix('').parts[0] != library:
            raise CanonError(f'module {relative} is outside the library; the modules of this canon are '
                             f'{library}.lean and the files under {library}/')
        if target.exists():
            raise CanonError(f'module {relative} already exists in the canon; a new module needs a new name')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(candidate / 'lean' / relative, target)
        changed.append('.'.join(PurePosixPath(relative).with_suffix('').parts))
    by_file = {}
    for item in change['replace']:
        entry = index['entries'].get(item['declaration'])
        if entry is None:
            raise CanonError(f'{item["declaration"]} is not a declaration of the canon; a new declaration goes in a new module')
        by_file.setdefault(entry['file'], []).append((entry, item))
    for relative, items in by_file.items():
        path = lean_root / relative
        held = path.read_text(encoding='utf-8').replace('\r\n', '\n')
        text = held
        # From the bottom up, so that earlier spans keep their line numbers.
        for entry, item in sorted(items, key=lambda pair: pair[0]['span'], reverse=True):
            current = declaration_text(text, entry['span'])
            if sha256_text(current) != entry['source_sha']:
                raise CanonError(f'the source of {entry["name"]} does not match the index; the index is stale')
            if bases.get(entry['name'], entry['source_sha']) != entry['source_sha']:
                raise replaced_since(entry['name'])
            replacement = (candidate / item['file']).read_text(encoding='utf-8-sig').replace('\r\n', '\n')
            text = replace_span(text, entry['span'], replacement)
        imports = [name for _, item in items for name in item['imports']]
        if imports:
            text = add_imports(text, imports)
        # A file whose text stays as it was is not written again. Written again it would lose the line endings the
        # canon holds it with, and the lock on the definition modules compares the bytes of a file
        # (check_definition_modules).
        if text != held:
            write_text(path, text)
        changed.append('.'.join(PurePosixPath(relative).with_suffix('').parts))
    return sorted(set(changed))


def replaced_since(name):
    return CanonError(f'the proof of {name} was replaced by another publication after this '
                      'candidate was written; the candidate has to be made again on the current canon')


def definition_modules(instance):
    """The modules that the root's module imported when the instance was created, directly or through one another.

    They hold the definitions the root was posed with, and no publication changes their files
    (check_definition_modules). They are read from the instance's first commit: the module of the root from
    the index of that commit, and the imports of each module from the header of its file there. The root's
    own module is not among them, and neither is a module that the root's module does not reach."""
    instance = Path(instance)
    meta = read_json(instance / 'instance.json')
    commit = first_commit(instance)
    root_module = json.loads(git(instance, 'show', commit + ':canon/index.json'))['entries'][meta['root']]['module']
    reached, pending = set(), [root_module]
    while pending:
        module = pending.pop()
        if module in reached:
            continue
        reached.add(module)
        header = git(instance, 'show', f'{commit}:canon/lean/{module_file(module)}').replace('\r\n', '\n').split('\n')
        pending += [name for name in header_scan(header)[2] if name.split('.')[0] == meta['library']]
    return sorted(reached - {root_module})


def check_definition_modules(instance, lean_root, modules):
    """Refuse an application that changed the file of a definition module.

    lean_root is a copy of the canon's module root to which a candidate was applied, and `modules` are the
    modules the application wrote or removed there. A candidate changes a module when the file under
    lean_root is no longer, byte for byte, the file the canon holds; a module the canon does not have is new
    and is none of the definition modules. Git is asked for the definition modules only when the candidate
    changes a module, so a candidate that only adds modules costs nothing here."""
    held = Canon(instance).lean
    changed = [module for module in modules if (held / module_file(module)).is_file() and not (
        (Path(lean_root) / module_file(module)).is_file()
        and (Path(lean_root) / module_file(module)).read_bytes() == (held / module_file(module)).read_bytes())]
    locked = sorted(set(changed) & set(definition_modules(instance))) if changed else []
    if locked:
        raise CanonError(
            'the candidate changes the file of ' + ', '.join(locked) + ". The modules that the root's module "
            'imported when the instance was created hold the definitions the root was posed with, and their files '
            'do not change. A new proof of a statement that stands in such a module enters as a separate '
            'declaration in a new module, with "proves" in its record, and a rearrangement leaves such a module as '
            'it is')


def written_base(canon, name):
    """The identity of the proof as the canon's record of a declaration carries it.

    It covers the written proof and the statement the record says the declaration proves or refutes. With
    the Lean text of the declaration, these are what a replacement replaces (check_applied). A candidate can
    bring a new proof and leave the Lean text as it is, so `prepare` keeps this identity beside that of the
    Lean text for every declaration the candidate replaces."""
    record = read_record(canon, name)
    meta, sections = (record['meta'], record['sections']) if record else ({}, {})
    return sha256_text('\n'.join([meta.get('proves') or '', meta.get('refutes') or '',
                                  (sections.get('Proof') or '').strip()]))


def check_written_bases(canon, change, bases):
    """Refuse a replacement whose declaration another publication gave a new proof under the same Lean text.

    bases maps a replaced declaration to the written_base its record had when the candidate was prepared.
    apply_lean compares the Lean text in the same way and finds the proofs replaced with a new Lean text."""
    for item in change['replace']:
        name = item['declaration']
        if name in bases and bases[name] != written_base(canon, name):
            raise replaced_since(name)


def sync_tree(source, target):
    """Make a module root hold exactly the files of another, changing only the files that differ.

    The canon is read by running sessions, and on Windows a folder with an open file cannot be renamed.
    So the canon's module root is never swapped as a whole: each changed file is replaced by itself and
    a file that is gone from the source is removed, each with the runtime's retry for a file that a
    reader holds for a moment. Doing it again after an interruption completes it."""
    source, target = Path(source), Path(target)
    wanted = set()
    for path in sorted(p for p in source.rglob('*') if p.is_file()):
        relative = path.relative_to(source)
        wanted.add(relative.as_posix())
        destination = target / relative
        data = path.read_bytes()
        if destination.is_file() and destination.read_bytes() == data:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(destination.name + '.installing')
        # On the disk before it takes its name. The runner saves, through to the disk, that the publication is
        # installed and then removes the stage these files came from; after a loss of power the canon must not
        # hold, under that record, a file whose content never arrived there.
        with temporary.open('wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        replace_file(temporary, destination)
    for path in sorted(p for p in target.rglob('*') if p.is_file()):
        if path.relative_to(target).as_posix() not in wanted:
            remove_file(path)


def copy_tree(source, target):
    """A fresh copy of a module root; the copy is what a session or the runner builds."""
    target = Path(target)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)


def copy_canon(instance, target, revision):
    """A fresh copy of the canon's module root, as copy_tree makes it, for a command that read the index at
    `revision`; CanonError when the copy cannot be taken for the library of that revision.

    The runner puts a publication into the canon while sessions run their commands: each changed module by
    itself, then the removal of each module that is gone, then the index (Runner.install_canon). A copy made
    meanwhile can hold one module as the publication leaves it and another as it was, or fail on a file that
    went away under it, and what is built on it then fails for a reason that is in no file of the session.
    The runner saves that a publication has reached the stage `commit` before it writes into the canon, and
    that it is installed once the index is in place (Runner.publish). So the saved state is read after the
    copy, and the index after the state. A publication that changes or removes a module and stands between
    those two saves, under a runner that is alive, can have been written under the copy. An index with
    another revision was put in place after the caller read it. The state is read first, so that an
    installation which ends between the two reads shows in the index. A runner that ended inside an
    installation writes nothing more: the canon stays as it left it until the next runner starts, and a copy
    is then kept, as every other command goes on reading that canon."""
    instance = Path(instance)
    canon = Canon(instance)
    failed = None
    try:
        copy_tree(canon.lean, target)
    except OSError as exc:
        failed = exc
    publication = read_json(instance / 'runner/state.json').get('publication') or {}
    receipt = instance / 'runner/process.json'
    installing = (publication.get('stage') == 'commit' and not publication.get('installed')
                  and bool(publication.get('changed') or publication.get('removed'))
                  and receipt.exists() and alive(read_json(receipt)['process']))
    if installing or canon.load_index()['revision'] != revision:
        shutil.rmtree(target, ignore_errors=True)
        raise CanonError('a publication was put into the canon, or was being put there, while this command read '
                         'it, so its copy of the library was not kept; run the command again')
    if failed is not None:
        raise failed


# ----------------------------------------------------------------------------- extraction

def lean_name(name):
    return '`' + name


def extraction_source(library, modules, pairs, imports=None):
    """A plain Lean file that prints one JSON row for every constant of the named modules.

    It is not a `module` file, so it reads the private data of the modules it imports and sees the
    proof terms. A row gives what Lean alone can know: the kind, the source span, the printed
    statement, the canon constants the statement and the proof use, the library theorems the proof
    uses, whether the constant's own term contains `sorry`, and the axioms the constant depends on.

    The axioms are the answer of `Lean.collectAxioms`, the function behind `#print axioms`: every
    axiom reached from the constant through everything it uses, in the canon and in the imported
    library alike, in the environment this file loads. No other part of do-math works out axioms.
    Lean 4.36 keeps that answer for every declaration in the compiled module, so asking costs a
    lookup. The answer for a declaration of a module is as current as the module's compiled form:
    it changes only when the module is compiled again, and the broker compiles a module again
    whenever the compiled output of a module it imports changed, which includes a change in the
    axioms of any declaration there (lean_broker.module_key). The modules to extract are therefore
    the changed ones and every module that imports one of them (with_importers).

    Which rows are elements, and how auxiliary declarations fold into them, is decided in update_index.
    A pair asks whether two declarations state the same proposition, or whether one states the negation
    of the other. Lean finds a declaration only in a module the file imports, directly or through others.
    The file imports `imports` when it is given, which can name more modules than those extracted, and
    the extracted modules otherwise.

    The rows are printed by one command that visits every constant once. Lean limits the work of a
    command by default, and that limit is lifted for this one: its work grows with the canon, and a
    canon of a few thousand constants passed the default after a third of its rows, every time."""
    imports = '\n'.join('import ' + m for m in (modules if imports is None else imports))
    targets = ', '.join(lean_name(m) for m in modules)
    listed = ', '.join(f'("{kind}", {lean_name(a)}, {lean_name(b)})' for kind, a, b in pairs)
    return f'''import Lean
{imports}
open Lean Meta

namespace {EXTRACT_MODULE}

def targets : Array Name := #[{targets}]
def library : Name := {lean_name(library)}
def pairs : Array (String × Name × Name) := #[{listed}]

def fnv (seed : UInt64) (s : String) : UInt64 :=
  s.foldl (fun h c => (h ^^^ c.toNat.toUInt64) * 1099511628211) seed

def moduleOf (env : Environment) (c : Name) : Option Name :=
  (env.getModuleIdxFor? c).map fun i => env.header.moduleNames[i.toNat]!

def inCanon (env : Environment) (c : Name) : Bool :=
  match moduleOf env c with
  | some m => m.getRoot == library
  | none => false

def kindOf (ci : ConstantInfo) : String :=
  match ci with
  | .thmInfo _ => "theorem" | .defnInfo _ => "def" | .axiomInfo _ => "axiom"
  | .opaqueInfo _ => "opaque" | .inductInfo _ => "inductive" | .ctorInfo _ => "ctor"
  | .recInfo _ => "rec" | .quotInfo _ => "quot"

def row (env : Environment) (name : Name) (ci : ConstantInfo) : MetaM Json := do
  let ranges ← findDeclarationRanges? name
  let span : Json := match ranges with
    | some r => toJson #[r.range.pos.line, r.range.pos.column, r.range.endPos.line, r.range.endPos.column]
    | none => Json.null
  let value : Array Name := match ci with
    | .thmInfo v => v.value.getUsedConstants
    | .defnInfo v => v.value.getUsedConstants
    | .opaqueInfo v => v.value.getUsedConstants
    | .inductInfo v => v.ctors.toArray
    | _ => #[]
  let typeUses := ci.type.getUsedConstants
  let used := typeUses ++ value
  let mut lib : Array Name := #[]
  for d in used do
    if !inCanon env d then
      if let some (.thmInfo _) := env.find? d then
        if !lib.contains d then lib := lib.push d
  let axioms ← collectAxioms name
  let sig ← try
      let f ← (PrettyPrinter.ppSignature name : MetaM _)
      pure (f.fmt.pretty 100)
    catch _ => pure (toString (← ppExpr ci.type))
  let text := toString ci.type ++ "|" ++ toString ci.levelParams.length
  let prop ← try isProp ci.type catch _ => pure false
  return Json.mkObj [
    ("name", toString name), ("kind", kindOf ci), ("module", toString ((moduleOf env name).getD .anonymous)),
    ("private", isPrivateName name), ("internal", (privateToUserName name).isInternal),
    ("user", toString (privateToUserName name)), ("span", span), ("sig", sig), ("prop", prop),
    ("statement", toString (fnv 14695981039346656037 text) ++ "-" ++ toString (fnv 1099511628211 text)),
    ("type_uses", toJson ((typeUses.filter (inCanon env)).map toString)),
    ("value_uses", toJson ((value.filter (inCanon env)).map toString)),
    ("library", toJson (lib.map toString)), ("sorry", used.contains ``sorryAx),
    ("collected", toJson (axioms.map toString))]

def samePair (env : Environment) (kind : String) (a b : Name) : Bool :=
  match env.find? a, env.find? b with
  | some ca, some cb =>
    if ca.levelParams.length != cb.levelParams.length then false
    else
      let ta := ca.type.instantiateLevelParams ca.levelParams (cb.levelParams.map mkLevelParam)
      if kind == "negation" then ta == mkApp (mkConst ``Not) cb.type else ta == cb.type
  | _, _ => false

def run : MetaM Unit := do
  let env ← getEnv
  for (name, ci) in env.constants.map₁.toList do
    if let some m := moduleOf env name then
      if targets.contains m then
        IO.println ("{ROW_MARK}" ++ (← row env name ci).compress)
  for (kind, a, b) in pairs do
    IO.println ("{ROW_MARK}" ++ (Json.mkObj [("pair", kind), ("a", toString a), ("b", toString b),
      ("holds", samePair env kind a b)]).compress)
  IO.println ("{ROW_MARK}" ++ (Json.mkObj [("done", true)]).compress)

set_option maxHeartbeats 0 in
#eval run

end {EXTRACT_MODULE}
'''


# The identity of the extraction file apart from the modules and pairs it is asked about. A build that
# was staged with another extraction printed rows of another form, so whoever kept such a build stages
# it again: the runner for a publication, `prepare` and `verify` for a candidate.
EXTRACTION = sha256_text(extraction_source('', [], []))[:16]


def parse_rows(output):
    """The rows an extraction printed, or an error when its last line never came."""
    rows, pairs, done = [], {}, False
    for line in output.splitlines():
        if not line.startswith(ROW_MARK):
            continue
        row = json.loads(line[len(ROW_MARK):])
        if 'done' in row:
            done = True
        elif 'pair' in row:
            pairs[row['pair'] + '|' + row['a'] + '|' + row['b']] = bool(row['holds'])
        else:
            rows.append(row)
    if not done:
        raise CanonError('the extraction did not finish; read its Lean output')
    return rows, pairs


def is_prefix(shorter, longer):
    a, b = name_parts(shorter), name_parts(longer)
    return len(a) < len(b) and b[:len(a)] == a


def contains(outer, inner):
    return (outer[0], outer[1]) <= (inner[0], inner[1]) and (inner[2], inner[3]) <= (outer[2], outer[3])


def update_index(index, rows, pairs, lean_root, revision, modules=()):
    """The structural index after the named modules were extracted again.

    The rows replace everything the index held for the modules extracted, which are those named and
    those of the rows; a module that now declares nothing has no rows. An entry is a declaration the
    author wrote: it has a source span, a public name, and its span is not inside the span of a
    declaration whose name it extends (a structure's fields and constructor are inside the
    structure). Every other constant of the canon is auxiliary. An auxiliary whose name extends an
    entry of its own module belongs to that entry: it counts as that entry wherever it is used, and
    what it uses is the entry's as well. An auxiliary that belongs to no entry, such as a private
    helper, is replaced by what it uses. The index keeps under `hidden` what each such auxiliary was
    replaced by, because a later extraction of another module has to pass through it and no longer
    has its row.

    Two things are recorded about an entry's proof, and they answer different questions.

    `axioms` is what Lean reported for the declaration (the row's `collected`): every axiom its proof
    depends on through everything it uses. It is stored as Lean gave it and nothing is added to it
    here. A statement is formal when this list lies within the allowed axioms (beyond_allowed), so a
    `sorry` anywhere below it, an axiom the author declared, and the axiom that `native_decide`
    generates for each computation all keep it from being formal.

    `lean_proof` says whether the declaration's own proof is written out: `sorry` when the term of the
    declaration, or of an auxiliary that is folded into it, contains `sorry`, and `complete` otherwise.
    It does not look into the entries the proof names. A proof that is complete and names a statement
    still open is a proof, of this statement from that one, and the standing of statements and the
    frontier are built on that.

    `hidden` also names every axiom of the canon that is no entry, whether the author wrote it as
    private or Lean generated it, because a candidate that declares an axiom is refused (check_applied)."""
    lean_root = Path(lean_root)
    modules = sorted(set(modules) | {row['module'] for row in rows})
    entries = {name: entry for name, entry in index['entries'].items() if entry['module'] not in modules}
    aux = {name: parent for name, parent in index['aux'].items() if parent is None or parent in entries}
    hidden = {name: item for name, item in index.get('hidden', {}).items() if item['module'] not in modules}
    raw = {row['name']: row for row in rows}
    candidates = [row for row in rows if row['span'] and not row['private'] and not row['internal']
                  and row['kind'] in ENTRY_KINDS]
    # A declaration stands inside another only within one module, so a row is held against the rows of its
    # own module and not against every row of the extraction, whose number grows with the library.
    by_module = {}
    for row in candidates:
        by_module.setdefault(row['module'], []).append(row)
    new = {}
    for row in candidates:
        inside = any(is_prefix(other['name'], row['name']) and contains(other['span'], row['span'])
                     for other in by_module[row['module']] if other is not row)
        if not inside:
            new[row['name']] = row
    known = set(entries) | set(new)

    def parent(row):
        # Only an entry of the same module: that entry is extracted together with the auxiliary, so
        # what the auxiliary uses can be made the entry's. An entry elsewhere is not touched.
        parts = name_parts(row['user'])
        for length in range(len(parts) - 1, 0, -1):
            prefix = '.'.join(parts[:length])
            if prefix in new and new[prefix]['module'] == row['module']:
                return prefix
        return None

    for row in rows:
        if row['name'] not in new:
            aux[row['name']] = parent(row)

    def resolve(name, owner, seen, into, folded):
        """Add to `into` the entries that a used canon constant stands for, seen from `owner`.

        `folded` receives what the auxiliaries passed through on the way bring with them: the library
        theorems they use, and whether one of them contains `sorry`."""
        if name in known:
            if name != owner:
                into.add(name)
            return
        target = aux.get(name)
        if target is not None and target != owner:
            into.add(target)
            return
        if name in seen:
            return
        row = raw.get(name)
        if row is None:
            # An auxiliary of a module that is not extracted now: what it was replaced by when its module was.
            kept = hidden.get(name)
            if kept is not None:
                seen.add(name)
                folded['sorry'] = folded['sorry'] or kept['sorry']
                folded['library'].update(kept['library'])
                into.update(used for used in kept['uses'] if used != owner)
            return
        seen.add(name)
        folded['sorry'] = folded['sorry'] or row['sorry']
        folded['library'].update(row['library'])
        for used in row['type_uses'] + row['value_uses']:
            resolve(used, owner, seen, into, folded)

    # The auxiliaries that belong to each entry, in the order of the rows. They are gathered once, so that an
    # extraction of the whole library does not go through every row again for every entry.
    owned = {}
    for child in rows:
        owner = aux.get(child['name'])
        if owner is not None:
            owned.setdefault(owner, []).append(child['name'])
    for name, row in new.items():
        statement_uses, uses = set(), set()
        folded = {'library': set(row['library']), 'sorry': row['sorry']}
        seen = {name}
        for used in row['type_uses']:
            resolve(used, name, seen, statement_uses, folded)
        for used in row['value_uses']:
            resolve(used, name, seen, uses, folded)
        for child in owned.get(name, ()):
            if child not in seen:
                resolve(child, name, seen, uses, folded)
        relative = module_file(row['module'])
        text = (lean_root / relative).read_text(encoding='utf-8').replace('\r\n', '\n')
        entries[name] = {
            'name': name, 'kind': row['kind'], 'module': row['module'], 'file': relative, 'span': row['span'],
            'source_sha': sha256_text(declaration_text(text, row['span'])),
            'statement': row['sig'], 'statement_hash': row['statement'], 'prop': bool(row['prop']),
            'statement_uses': sorted(statement_uses), 'uses': sorted(uses - {name}),
            'library': sorted(folded['library']), 'axioms': sorted(row['collected']),
            'lean_proof': None if row['kind'] not in ('theorem', 'def', 'opaque')
            else 'sorry' if folded['sorry'] else 'complete'}
    for row in rows:
        name = row['name']
        if name in new or (aux.get(name) is not None and row['kind'] != 'axiom'):
            continue
        uses, folded = set(), {'library': set(), 'sorry': False}
        if aux.get(name) is None:
            resolve(name, None, set(), uses, folded)
        hidden[name] = {'module': row['module'], 'user': row['user'], 'axiom': row['kind'] == 'axiom',
                        'generated': bool(row['internal']), 'uses': sorted(uses),
                        'library': sorted(folded['library']), 'sorry': folded['sorry']}
    table = dict(index['modules'])
    for module in modules:
        relative = module_file(module)
        if (lean_root / relative).is_file():
            table[module] = {'file': relative, 'sha256': hashlib.sha256((lean_root / relative).read_bytes()).hexdigest()}
        else:
            table.pop(module, None)
    return {'revision': revision, 'modules': table, 'entries': entries, 'aux': aux, 'hidden': hidden,
            'pairs': {**index.get('pairs', {}), **pairs}}


def drop_modules(index, modules):
    """The index without the entries of modules that no longer exist."""
    modules = set(modules)
    entries = {n: e for n, e in index['entries'].items() if e['module'] not in modules}
    return {**index, 'entries': entries,
            'modules': {m: v for m, v in index['modules'].items() if m not in modules},
            'aux': {n: p for n, p in index['aux'].items() if p is None or p in entries},
            'hidden': {n: item for n, item in index.get('hidden', {}).items() if item['module'] not in modules}}


def beyond_allowed(entry, allowed):
    """What keeps a statement from being proved in Lean from the allowed axioms; empty when it is so proved.

    These are the axioms Lean reported for the declaration that are not allowed: `sorryAx` for a `sorry`
    anywhere below it, an axiom declared in the canon, the axiom of a `native_decide`. `sorryAx` is
    named as well when the declaration's own proof is not complete although Lean's list is without it.
    That happens when the `sorry` stands in an auxiliary declared under the entry's name which the
    entry's own term does not reach: the auxiliary's open proof counts as the entry's (update_index)."""
    found = set(entry['axioms']) - set(allowed)
    if entry['lean_proof'] == 'sorry':
        found.add('sorryAx')
    return sorted(found)


def statement_differences(first, now, name):
    """How a statement, with every definition under it, differs between two indexes of one canon.

    `first` is the index as the instance's first commit has it and `now` the index as it stands. The
    result is empty when the statement of `name` is the same in both, and otherwise says what differs.
    The comparison starts at `name` and goes to every entry its statement names, and from a definition
    also to what its body names, since the body of a definition is part of what a statement built on it
    says. A theorem met on the way counts by its statement alone, whatever its proof became. Each entry
    reached must be in both indexes with the same kind and the same statement, by the identity Lean's
    term has (`statement_hash`), and a definition also with the same source text (`source_sha`). What
    is reached is followed in both indexes, so a dependency that exists only now is found as well.

    The comparison reads the two indexes and compiles nothing. What it cannot see is a declaration
    that is no entry, such as a private helper of a definition, and a definition whose unchanged text
    Lean would read as another term."""
    before, after = first['entries'], now['entries']
    found, reached, pending = [], set(), [name]
    while pending:
        current = pending.pop()
        if current in reached:
            continue
        reached.add(current)
        old, new = before.get(current), after.get(current)
        if old is None or new is None:
            found.append(f'{current} is under the statement and is not in the canon '
                         + ('of the first commit' if old is None else 'as it stands'))
        elif old['kind'] != new['kind']:
            found.append(f"{current} was declared as {old['kind']} and is now declared as {new['kind']}")
        elif old['statement_hash'] != new['statement_hash']:
            found.append(f'the statement of {current} is not the statement the first commit has')
        elif old['kind'] not in STATEMENT_KINDS and old['source_sha'] != new['source_sha']:
            found.append(f'the text of the definition {current} is not the text the first commit has')
        for entry in (old, new):
            if entry is not None:
                pending += entry['statement_uses'] + ([] if entry['kind'] in STATEMENT_KINDS else entry['uses'])
    return sorted(found)


# ----------------------------------------------------------------------------- building through the broker

def start_build(instance, lean_root, library, session, expect_mb, extract, pairs, fresh=False, targets=None,
                index=None):
    """Queue one broker build of the library under lean_root, with an extraction of the named modules.

    The extraction file is one more target of the same build, so it is compiled after the modules it
    imports and its output is kept with the build like any target's. A pair can name a declaration in a
    module that no extracted module imports: a new proof in a new module need not import the module of
    the statement its record says it proves or refutes. An extraction asked about pairs therefore imports
    the modules of the declarations its pairs name as well. `index` is the index of the canon that the
    tree under lean_root was copied from, and it gives the module of each declaration that canon has. A
    module the change left as it was still holds its declarations. A declaration the change brought or
    moved stands in a module the change wrote, and such a module is among the extracted ones
    (with_importers). The compile of the extraction loads every module the file imports, with its
    proofs, so the file imports these modules and no others. Without `index` it imports every module of
    the library. Returns the build ID."""
    from lean_broker import Paths, build
    lean_root = Path(lean_root)
    names = [module for module, _ in library_modules(lean_root, library)]
    if not names:
        raise CanonError(f'no module of the library {library} under {lean_root}')
    files = [str(lean_root / module_file(m)) for m in (targets if targets is not None else names)]
    if extract or pairs:
        imports = None
        if pairs and index is None:
            imports = names
        elif pairs:
            named = {index['entries'][name]['module'] for _, declaration, target in pairs
                     for name in (declaration, target) if name in index['entries']}
            imports = sorted(set(extract) | (named & set(names)))
        write_text(lean_root / (EXTRACT_MODULE + '.lean'), extraction_source(library, extract, pairs, imports))
        files.append(str(lean_root / (EXTRACT_MODULE + '.lean')))
    return build(Paths(instance), lean_root, files, expect_mb, session, fresh_targets=fresh)['build']


def build_outcome(instance, build_id):
    """None while the build runs; afterwards whether it succeeded, what failed, and the extracted rows."""
    from lean_broker import FINISHED, Paths, job_record
    paths = Paths(instance)
    record = job_record(paths, build_id)
    if record is None:
        raise CanonError('unknown build: ' + build_id)
    if record['status'] == 'duplicate':
        return build_outcome(instance, record['duplicate_of'])
    if record['status'] not in FINISHED:
        return None

    def logs(entry):
        if entry.get('job'):
            folder = paths.job(entry['job'])
            return folder / 'stdout.log', folder / 'stderr.log'
        return paths.cache / (entry['key'] + '.stdout.log'), paths.cache / (entry['key'] + '.stderr.log')

    def read(path):
        return path.read_text(encoding='utf-8', errors='replace') if path.is_file() else ''

    errors = []
    modules = record.get('modules', {})
    for name, entry in modules.items():
        good = entry.get('status') == 'cached' or (entry.get('status') == 'finished' and entry.get('exit_code') == 0)
        if not good:
            out, err = logs(entry) if entry.get('job') or entry.get('key') else (None, None)
            text = ((read(out) if out else '') + (read(err) if err else '')).strip()
            errors.append({'module': name, 'status': entry.get('status'), 'exit_code': entry.get('exit_code'),
                           'reason': entry.get('reason'), 'output': text[-4000:]})
    if record['status'] != 'finished' and not errors:
        errors.append({'module': None, 'status': record['status'], 'reason': record.get('reason'), 'output': ''})
    outcome = {'ok': not errors, 'build': record['id'], 'errors': errors, 'rows': [], 'pairs': {}}
    if outcome['ok'] and EXTRACT_MODULE in modules:
        try:
            outcome['rows'], outcome['pairs'] = parse_rows(read(logs(modules[EXTRACT_MODULE])[0]))
        except (CanonError, ValueError) as exc:
            outcome.update(ok=False, errors=[{'module': EXTRACT_MODULE, 'status': 'failed', 'reason': str(exc), 'output': ''}])
    return outcome


def wait_build(instance, build_id, timeout=None):
    """The outcome of a build, or None when the timeout passes first; the build continues either way.

    A build makes progress only while a broker is alive. Like the broker's own `wait`, this asks for
    one every few seconds, and reports that none came instead of waiting without end. The waiting is
    the broker client's (`lean_broker.await_record`), which looks for the build's result file and does
    not read the broker's whole state at every look."""
    from lean_broker import Paths, await_record
    outcome = build_outcome(instance, build_id)
    if outcome is not None:
        return outcome
    _, _, ended = await_record(Paths(instance), build_id, timeout)
    return build_outcome(instance, build_id) if ended else None


# ----------------------------------------------------------------------------- validating a candidate against its index

def required_pairs(records_by_path):
    """The (kind, declaration, target) pairs that records claim: another proof of, or a refutation of."""
    pairs = []
    for path, record in records_by_path.items():
        name = path_name(path)
        if record['meta'].get('proves'):
            pairs.append(('same', name, record['meta']['proves']))
        if record['meta'].get('refutes'):
            pairs.append(('negation', name, record['meta']['refutes']))
    return pairs


def candidate_records(candidate, change):
    """The candidate's records by the name path of their file."""
    result = {}
    for relative in change['records']:
        text = (Path(candidate) / 'records' / relative).read_text(encoding='utf-8-sig')
        result[relative[:-3]] = parse_record(text, 'records/' + relative)
    return result


def check_applied(old, new, change, records_by_path, existing_record, allowed_axioms, organizer=False):
    """What a candidate added and replaced, and the reasons it cannot be published as it is.

    old and new are the index before and after the candidate. records_by_path maps the name path
    of each candidate record to the record; existing_record(name) gives the record the canon has
    for a declaration, or nothing. The checks are those a machine can decide: a statement that
    changed in place, a proof changed without a replacement, a declaration without a record, a
    record without a declaration, a claim of another proof or a refutation that Lean did not
    confirm, an axiom, a definition left open."""
    errors = []
    added = sorted(set(new['entries']) - set(old['entries']))
    removed = sorted(set(old['entries']) - set(new['entries']))
    replaced = sorted(item['declaration'] for item in change['replace'])
    retired = {item['alternative'] for item in change['retire']} if organizer else set()
    moved = {item['alternative']: item['into'] for item in change['retire']} if organizer else {}
    if set(removed) - retired:
        errors.append('declarations disappeared from the canon: ' + ', '.join(sorted(set(removed) - retired)))
    for item in change['retire'] if organizer else []:
        before, after = old['entries'].get(item['alternative']), new['entries'].get(item['into'])
        if item['alternative'] in new['entries'] or before is None or after is None:
            errors.append(f"retiring {item['alternative']} into {item['into']} needs the first removed and the second kept")
        elif (sorted(set(after['uses']) - {item['alternative']})
              != sorted({moved.get(u, u) for u in before['uses']} - {item['into']})
              or after['lean_proof'] != before['lean_proof']):
            errors.append(f"after retiring {item['alternative']}, the proof of {item['into']} does not name what "
                          'the retired proof named; a retirement moves a proof and does not change it')
    for name in sorted(set(new['entries']) & set(old['entries'])):
        before, after = old['entries'][name], new['entries'][name]
        if before['statement_hash'] != after['statement_hash'] or before['kind'] != after['kind']:
            if before['kind'] == after['kind'] and before['source_sha'] == after['source_sha']:
                # The text is the one the canon has, and Lean turns it into another term now: the change
                # enlarged what this declaration's module imports, directly or through a module it imports
                # (with_importers). The check sees a different term and cannot say whether the meaning
                # differs. In the one case met so far it did not: an added Mathlib import made `C ^ k` on
                # natural numbers in the root's statement elaborate through `Monoid.npow`.
                errors.append(f'the statement of {name} elaborates differently with this change although its text is '
                              f'unchanged: the change enlarges what the module of {name} imports, directly or through '
                              'a module it imports, and Lean then reads the same text as another term, for example '
                              'through another instance (an added Mathlib import has made `^` on natural numbers '
                              'elaborate through `Monoid.npow`). The meaning may be the same, but the statement is no '
                              'longer the term the canon has. Leave the imports of that module as they are: put what '
                              'the new proof needs into a new module and enter the proof there as a separate '
                              'declaration whose record says which statement it proves, or keep an instance or a '
                              'notation of your own `local` or `scoped`')
            else:
                errors.append(f'the statement of {name} changed in place; a different statement enters under a new name')
        elif name not in replaced and not organizer and before['source_sha'] != after['source_sha']:
            errors.append(f'the source of {name} changed although the candidate does not replace it')
        if name in replaced and after['kind'] != 'theorem' and before['source_sha'] != after['source_sha']:
            errors.append(f'{name} is a definition; a definition is not replaced in place, because what '
                          'uses it would change its meaning')
        if organizer and name not in moved.values():
            # A rearrangement moves declarations and turns references to a retired declaration into
            # references to the statement's own. Anything else it did to an element would be a change
            # of mathematics that no review has seen.
            if after['kind'] != 'theorem':
                if before['source_sha'] != after['source_sha']:
                    errors.append(f'the text of the definition {name} changed; a rearrangement moves a '
                                  'definition and does not rewrite it')
            elif (after['lean_proof'] != before['lean_proof']
                  or sorted(set(after['uses']) - {name}) != sorted({moved.get(u, u) for u in before['uses']} - {name})):
                errors.append(f'the proof of {name} changed in what it names or in whether it is complete; apart '
                              'from references to a retired declaration, a rearrangement leaves every proof as it was')
    paths = {name_path(name): name for name in new['entries']}
    records = {}
    for path, record in records_by_path.items():
        name = paths.get(path)
        if name is None:
            errors.append(f'records/{path}.md belongs to no declaration of the canon after this change')
        else:
            records[name] = record
    standing_modules = {entry['module'] for entry in old['entries'].values()}
    for name in added:
        if new['entries'][name]['module'] in standing_modules:
            errors.append(f"{name} is declared in {new['entries'][name]['module']}, a module the canon already has; "
                          'a new declaration goes in a new module')
    for group in case_collisions(new['entries']):
        if set(group) & set(added):
            errors.append('the names ' + ', '.join(group) + ' differ only in the case of their letters, and their '
                          'records would be one file where the file system ignores case; choose another name')
    for item in change['retire'] if organizer else []:
        after = new['entries'].get(item['into'])
        if after is not None and after['lean_proof'] != 'complete':
            record = records.get(item['into']) or existing_record(item['into'])
            if not (record and record['sections'].get('Proof')):
                errors.append(f"after retiring {item['alternative']}, the record of {item['into']} needs the written "
                              'proof that stood in the record of the retired declaration, as its "## Proof"')
    for name in added:
        entry = new['entries'][name]
        if name not in records:
            errors.append(f'{name} has no record; write records/{name_path(name)}.md')
        if entry['kind'] == 'axiom':
            errors.append(f'{name} is declared as an axiom; state it as a theorem and leave its proof open instead')
        if entry['kind'] in ('def', 'opaque') and entry['lean_proof'] == 'sorry':
            errors.append(f'the definition {name} contains sorry; a definition has to be complete')
    for name, item in sorted(new.get('hidden', {}).items()):
        # An axiom the author wrote without making it an element. One that Lean generated has an internal
        # name; it is not refused, and what rests on it is simply not proved from the allowed axioms.
        if item['axiom'] and not item['generated'] and name not in old.get('hidden', {}):
            errors.append(f"{item['user']} is declared as an axiom in {item['module']}; state it as a theorem "
                          'and leave its proof open instead')
    for name in replaced:
        if name in new['entries'] and name not in records and not existing_record(name):
            errors.append(f'{name} has no record; write records/{name_path(name)}.md')
    for name, record in records.items():
        entry = new['entries'][name]
        meta = record['meta']
        for key, kind in (('proves', 'same'), ('refutes', 'negation')):
            target = meta.get(key)
            if not target:
                continue
            if target not in new['entries']:
                errors.append(f'{name}: "{key}: {target}" names no declaration of the canon')
            elif entry['kind'] not in STATEMENT_KINDS or new['entries'][target]['kind'] not in STATEMENT_KINDS:
                # A definition has no standing (knowledge.settle), so neither end of the claim can be one.
                other = name if entry['kind'] not in STATEMENT_KINDS else target
                errors.append(f'{name}: "{key}: {target}" relates two theorems, and {other} is declared as '
                              f"{new['entries'][other]['kind']}; a statement is a theorem, and so is what proves "
                              'or refutes it')
            elif not new.get('pairs', {}).get(f'{kind}|{name}|{target}'):
                errors.append(f'{name}: Lean did not confirm that its statement is '
                              + ('the statement of ' if kind == 'same' else 'the negation of the statement of ') + target)
        current = existing_record(name) if name in old['entries'] and name not in replaced else None
        if current and name not in moved.values():
            # Whether an element has a written proof, and what it proves or refutes, decide its standing.
            # Review judges the elements a candidate adds and the proofs it replaces, so a record may
            # change these only for a declaration the candidate lists in "replace".
            same = ((current['sections'].get('Proof') or '').strip() == (record['sections'].get('Proof') or '').strip()
                    and all(current['meta'].get(key) == meta.get(key) for key in ('proves', 'refutes')))
            if not same:
                errors.append(f'{name}: the record changes the written proof, "proves" or "refutes" of an element '
                              'whose proof the candidate does not replace; list the declaration in "replace"')
        if organizer and name in added and entry['kind'] in STATEMENT_KINDS:
            foreign = beyond_allowed(entry, allowed_axioms)
            if foreign:
                errors.append(f'{name} is not proved in Lean from the allowed axioms: ' + ', '.join(foreign))
    return {'added': added, 'replaced': replaced, 'records': sorted(records), 'errors': errors,
            'retired': [{'alternative': item['alternative'], 'into': item['into']} for item in change['retire']]
            if organizer else []}


# ----------------------------------------------------------------------------- applying the written part

def history_entry(canon, name, kind, revision, change_id, old, new, pointer, folder=None):
    """What a replacement leaves behind: where the current text is, and how the old one differed."""
    folder = canon.history / (folder or name_path(name))
    folder.mkdir(parents=True, exist_ok=True)
    diff = '\n'.join(difflib.unified_diff(new.splitlines(), old.splitlines(), 'current', 'replaced', lineterm=''))
    write_text(folder / f'{revision:06d}-{kind}.md',
               f'# {name}: {kind} replaced at revision {revision} by {change_id}\n\n'
               f'The current text is at `{pointer}`. The difference below turns the current text into the '
               f'text that was replaced.\n\n```diff\n{diff}\n```\n')


def apply_written(canon, candidate, change, applied, revision, change_id, contribution, question_id=lambda qid: qid):
    """Put a candidate's records, approach entries, understanding texts, evidence and sources into the canon.

    A replaced text leaves its difference in the history. Review's assessment of what the work
    contributed is written into each approach entry and understanding text of the change, where a
    session choosing its work will read it. question_id gives the identity a question has now, so
    that a text written under the name of a question merged since goes to the surviving one."""
    candidate = Path(candidate)
    paths = {name_path(name): name for name in applied['records']}
    for relative in change['records']:
        name = paths.get(relative[:-3])
        if name is None:
            continue
        target = record_file(canon, name)
        text = (candidate / 'records' / relative).read_text(encoding='utf-8-sig').replace('\r\n', '\n')
        if target.exists():
            old = target.read_text(encoding='utf-8')
            if old != text:
                history_entry(canon, name, 'record', revision, change_id, old, text,
                              target.relative_to(canon.root).as_posix())
        target.parent.mkdir(parents=True, exist_ok=True)
        write_text(target, text)
    stamp = f'Change {change_id} (revision {revision}): {contribution.strip()}' if contribution else None
    for relative in change['approaches']:
        target = canon.approaches / relative
        text = with_review((candidate / 'approaches' / relative).read_text(encoding='utf-8-sig'), stamp)
        if target.exists():
            old = target.read_text(encoding='utf-8')
            if old != text:
                folder = PurePosixPath(relative).parent
                history_entry(canon, path_name(folder), 'approach-' + PurePosixPath(relative).stem, revision, change_id,
                              old, text, target.relative_to(canon.root).as_posix(), folder=folder)
        target.parent.mkdir(parents=True, exist_ok=True)
        write_text(target, text)
    for relative in change['understanding']:
        qid = question_id(PurePosixPath(relative).stem)
        target = canon.questions / (qid + '.md')
        text = with_review((candidate / 'questions' / relative).read_text(encoding='utf-8-sig'), stamp)
        if target.exists():
            old = target.read_text(encoding='utf-8')
            if old != text:
                folder = canon.history / 'questions' / qid
                folder.mkdir(parents=True, exist_ok=True)
                diff = '\n'.join(difflib.unified_diff(text.splitlines(), old.splitlines(), 'current', 'replaced', lineterm=''))
                write_text(folder / f'{revision:06d}.md',
                           f'# Question {qid}: understanding replaced at revision {revision} by {change_id}\n\n'
                           f'```diff\n{diff}\n```\n')
        target.parent.mkdir(parents=True, exist_ok=True)
        write_text(target, text)
    if (candidate / 'evidence').is_dir():
        for path in sorted(p for p in (candidate / 'evidence').rglob('*') if p.is_file()):
            target = canon.evidence / path.relative_to(candidate / 'evidence')
            target.parent.mkdir(parents=True, exist_ok=True)
            # Written beside the file, sent to the disk and moved onto it, as a module is installed (sync_tree): a
            # session that reads the evidence a record refers to has the earlier file or the new one, each of them
            # whole, and after a loss of power the canon holds no file whose content never arrived on the disk.
            temporary = target.with_name(target.name + '.installing')
            with path.open('rb') as source, temporary.open('wb') as stream:
                shutil.copyfileobj(source, stream)
                stream.flush()
                os.fsync(stream.fileno())
            replace_file(temporary, target)
    addition = candidate / 'bibliography.bib'
    if addition.is_file():
        merge_bibliography(canon.bibliography, addition.read_text(encoding='utf-8-sig'))


BIB_ENTRY = re.compile(r'@\w+\s*\{\s*([^,\s]+)\s*,')


def merge_bibliography(path, addition):
    """Add entries whose keys the bibliography does not have yet; an existing key keeps its entry."""
    current = path.read_text(encoding='utf-8') if path.exists() else ''
    present = set(BIB_ENTRY.findall(current))
    pieces = re.split(r'(?=^@)', addition.replace('\r\n', '\n'), flags=re.MULTILINE)
    added = []
    for piece in pieces:
        match = BIB_ENTRY.match(piece.strip())
        if match and match[1] not in present:
            present.add(match[1])
            added.append(piece.strip())
    if added:
        write_text(path, (current.rstrip() + '\n\n' if current.strip() else '') + '\n\n'.join(added) + '\n')


def retire_approaches(canon, name, revision):
    """When an element's proof is accepted, the approaches tried on it go to its history.

    The folder of an element also holds the folders of the elements whose names extend its name,
    such as `A.b` under `A`. Those are other elements, and their approaches stay where they are."""
    folder = canon.approaches / name_path(name)
    entries = sorted(folder.glob('*.md')) if folder.is_dir() else []
    if not entries:
        return False
    target = canon.history / name_path(name) / f'{revision:06d}-approaches'
    target.mkdir(parents=True, exist_ok=True)
    for path in entries:
        replace_file(path, target / path.name)
    if not any(folder.iterdir()):
        try:
            folder.rmdir()
        except PermissionError:
            # Windows removes no folder that a process holds, such as the current directory of a shell that
            # reads the canon. The entries are in the history, and a folder without entries holds no approach.
            pass
    return True


def read_record(canon, name):
    path = record_file(canon, name)
    if not path.is_file():
        return None
    try:
        return parse_record(path.read_text(encoding='utf-8-sig'), name)
    except CanonError:
        return None


def read_approaches(canon, name):
    """The approach entries of an element, by entry ID, in file order."""
    folder = canon.approaches / name_path(name)
    entries = {}
    if folder.is_dir():
        for path in sorted(folder.glob('*.md')):
            try:
                entries[path.stem] = parse_approach(path.read_text(encoding='utf-8-sig'), path.name)
            except CanonError:
                continue
    return entries
