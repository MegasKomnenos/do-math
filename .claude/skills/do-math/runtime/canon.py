"""The canon of an instance: one Lean library with a written record beside each declaration.

An element is a declaration of that library together with its record. This module holds what
every part of the runtime needs to know about the canon's files: where a record lives, how a
record, an approach entry and a candidate change are written, how a candidate is applied to
the library, and how the structural index is extracted from the compiled library by Lean.
It judges no mathematics. See ../reference/canon.md for the formats as a session uses them.

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
import argparse
import difflib
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import time

from runtime_support import read_json, write_json, write_text

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
IMPORT_LINE = re.compile(r'^(?:public\s+)?(?:meta\s+)?import\s+(?:all\s+)?(\S+)')


class CanonError(ValueError):
    """A candidate or a canon file that the runtime cannot carry; the message says what to correct."""


class Conflict(CanonError):
    """The canon changed under a candidate in a way the candidate cannot be applied to."""


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
        return read_json(self.index) if self.index.exists() else empty_index()


def empty_index():
    return {'revision': 0, 'modules': {}, 'entries': {}, 'aux': {}, 'pairs': {}}


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
    parts, current, body = {}, None, []
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
            name_parts(meta[key])
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


# ----------------------------------------------------------------------------- Lean sources

def header_scan(lines):
    """The index after the last import line of a Lean file's header, whether it is a `module` file, and its imports."""
    last, module, depth, imports = 0, False, 0, []
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
                depth, index = 1, index + 2
            else:
                code.append(line[index])
                index += 1
        stripped = ''.join(code).strip()
        if not stripped:
            continue
        if stripped == 'module':
            module, last = True, number + 1
        elif stripped == 'prelude':
            last = number + 1
        elif found := IMPORT_LINE.match(stripped):
            last = number + 1
            imports.append(found[1])
        else:
            break
    return last, module, imports


def header_end(lines):
    """The index after the last import line of a Lean file's header, and whether it is a `module` file."""
    return header_scan(lines)[:2]


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
    files = lambda folder, suffix: sorted(p.relative_to(candidate / folder).as_posix()
                                          for p in (candidate / folder).rglob('*' + suffix) if p.is_file())
    data['modules'] = files('lean', '.lean')
    data['records'] = files('records', '.md')
    data['approaches'] = files('approaches', '.md')
    data['understanding'] = files('questions', '.md')
    for relative in data['records']:
        parse_record((candidate / 'records' / relative).read_text(encoding='utf-8-sig'), 'records/' + relative)
    for relative in data['approaches']:
        entry = parse_approach((candidate / 'approaches' / relative).read_text(encoding='utf-8-sig'),
                               'approaches/' + relative)
        if REVIEW_SECTION in entry['sections']:
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


def record_names(change):
    """Declaration name paths of the candidate's records, as the candidate wrote them."""
    return [relative[:-3] for relative in change['records']]


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
            raise Conflict(f'module {relative} already exists in the canon; a new module needs a new name')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(candidate / 'lean' / relative, target)
        changed.append('.'.join(PurePosixPath(relative).with_suffix('').parts))
    by_file = {}
    for item in change['replace']:
        entry = index['entries'].get(item['declaration'])
        if entry is None:
            raise Conflict(f'{item["declaration"]} is not a declaration of the canon; a new declaration goes in a new module')
        by_file.setdefault(entry['file'], []).append((entry, item))
    for relative, items in by_file.items():
        path = lean_root / relative
        text = path.read_text(encoding='utf-8').replace('\r\n', '\n')
        # From the bottom up, so that earlier spans keep their line numbers.
        for entry, item in sorted(items, key=lambda pair: pair[0]['span'], reverse=True):
            current = declaration_text(text, entry['span'])
            if sha256_text(current) != entry['source_sha']:
                raise Conflict(f'the source of {entry["name"]} does not match the index; the index is stale')
            if bases.get(entry['name'], entry['source_sha']) != entry['source_sha']:
                raise Conflict(f'the proof of {entry["name"]} was replaced by another publication after this '
                               'candidate was written; the candidate has to be made again on the current canon')
            replacement = (candidate / item['file']).read_text(encoding='utf-8-sig').replace('\r\n', '\n')
            text = replace_span(text, entry['span'], replacement)
        imports = [name for _, item in items for name in item['imports']]
        if imports:
            text = add_imports(text, imports)
        write_text(path, text)
        changed.append('.'.join(PurePosixPath(relative).with_suffix('').parts))
    return sorted(set(changed))


def sync_tree(source, target):
    """Make a module root hold exactly the files of another, changing only the files that differ.

    The canon is read by running sessions, and on Windows a folder with an open file cannot be renamed.
    So the canon's module root is never swapped as a whole: each changed file is replaced by itself,
    with the runtime's retry for a file that a reader holds for a moment, and a file that is gone from
    the source is removed. Doing it again after an interruption completes it."""
    from runtime_support import _replace_file
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
        temporary.write_bytes(data)
        _replace_file(temporary, destination)
    for path in sorted(p for p in target.rglob('*') if p.is_file()):
        if path.relative_to(target).as_posix() not in wanted:
            path.unlink()


def copy_tree(source, target):
    """A fresh copy of a module root; the copy is what a session or the runner builds."""
    target = Path(target)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)


# ----------------------------------------------------------------------------- extraction

def lean_name(name):
    return '`' + name


def extraction_source(library, modules, pairs):
    """A plain Lean file that prints one JSON row for every constant of the named modules.

    It is not a `module` file, so it reads the private data of the modules it imports and sees the
    proof terms. A row gives what Lean alone can know: the kind, the source span, the printed
    statement, the canon constants the statement and the proof use, the library theorems the proof
    uses, and the axioms reached through the library. Which rows are elements, and how auxiliary
    declarations fold into them, is decided in build_index. A pair asks whether two declarations
    state the same proposition, or whether one states the negation of the other."""
    imports = '\n'.join('import ' + m for m in modules)
    targets = ', '.join(lean_name(m) for m in modules)
    listed = ', '.join(f'("{kind}", {lean_name(a)}, {lean_name(b)})' for kind, a, b in pairs)
    return f'''import Lean
{imports}
open Lean Meta

namespace {EXTRACT_MODULE}

def targets : Array Name := #[{targets}]
def library : Name := {lean_name(library)}
def pairs : Array (String × Name × Name) := #[{listed}]

structure St where
  memo : Std.HashMap Name Nat := {{}}
  axioms : Array Name := #[]

abbrev M := StateT St MetaM

def fnv (seed : UInt64) (s : String) : UInt64 :=
  s.foldl (fun h c => (h ^^^ c.toNat.toUInt64) * 1099511628211) seed

def moduleOf (env : Environment) (c : Name) : Option Name :=
  (env.getModuleIdxFor? c).map fun i => env.header.moduleNames[i.toNat]!

def inCanon (env : Environment) (c : Name) : Bool :=
  match moduleOf env c with
  | some m => m.getRoot == library
  | none => false

def children (ci : ConstantInfo) : Array Name :=
  match ci with
  | .defnInfo v => v.type.getUsedConstants ++ v.value.getUsedConstants
  | .thmInfo v => v.type.getUsedConstants ++ v.value.getUsedConstants
  | .opaqueInfo v => v.type.getUsedConstants ++ v.value.getUsedConstants
  | .inductInfo v => v.type.getUsedConstants ++ v.ctors.toArray
  | .ctorInfo v => v.type.getUsedConstants
  | .recInfo v => v.type.getUsedConstants
  | _ => #[]

def axiomBit (n : Name) : M Nat := do
  match (← get).axioms.findIdx? (· == n) with
  | some i => return i
  | none =>
    let i := (← get).axioms.size
    modify fun s => {{ s with axioms := s.axioms.push n }}
    return i

/-- The axioms a constant outside the canon depends on, as a set of bits; canon constants stop the walk. -/
partial def mask (env : Environment) (c : Name) : M Nat := do
  if inCanon env c then return 0
  if let some m := (← get).memo[c]? then return m
  modify fun s => {{ s with memo := s.memo.insert c 0 }}
  let some ci := env.find? c | return 0
  let mut m := 0
  if ci matches .axiomInfo _ then m := 1 <<< (← axiomBit c)
  for d in children ci do
    m := m ||| (← mask env d)
  modify fun s => {{ s with memo := s.memo.insert c m }}
  return m

def kindOf (ci : ConstantInfo) : String :=
  match ci with
  | .thmInfo _ => "theorem" | .defnInfo _ => "def" | .axiomInfo _ => "axiom"
  | .opaqueInfo _ => "opaque" | .inductInfo _ => "inductive" | .ctorInfo _ => "ctor"
  | .recInfo _ => "rec" | .quotInfo _ => "quot"

def row (env : Environment) (name : Name) (ci : ConstantInfo) : M Json := do
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
  let mut m := 0
  let mut lib : Array Name := #[]
  for d in typeUses ++ value do
    m := m ||| (← mask env d)
    if !inCanon env d then
      if let some (.thmInfo _) := env.find? d then
        if !lib.contains d then lib := lib.push d
  let axioms := (← get).axioms
  let reached := (List.range axioms.size).filterMap fun i => if m &&& (1 <<< i) != 0 then some axioms[i]! else none
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
    ("library", toJson (lib.map toString)), ("axioms", toJson (reached.map toString))]

def samePair (env : Environment) (kind : String) (a b : Name) : Bool :=
  match env.find? a, env.find? b with
  | some ca, some cb =>
    if ca.levelParams.length != cb.levelParams.length then false
    else
      let ta := ca.type.instantiateLevelParams ca.levelParams (cb.levelParams.map mkLevelParam)
      if kind == "negation" then ta == mkApp (mkConst ``Not) cb.type else ta == cb.type
  | _, _ => false

def run : M Unit := do
  let env ← getEnv
  for (name, ci) in env.constants.map₁.toList do
    if let some m := moduleOf env name then
      if targets.contains m then
        IO.println ("{ROW_MARK}" ++ (← row env name ci).compress)
  for (kind, a, b) in pairs do
    IO.println ("{ROW_MARK}" ++ (Json.mkObj [("pair", kind), ("a", toString a), ("b", toString b),
      ("holds", samePair env kind a b)]).compress)
  IO.println ("{ROW_MARK}" ++ (Json.mkObj [("done", true)]).compress)

#eval show MetaM Unit from do
  let _ ← run.run {{}}

end {EXTRACT_MODULE}
'''


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
    what it uses and the axioms it depends on are the entry's as well. An auxiliary that belongs to
    no entry, such as a private helper, is replaced by what it uses."""
    lean_root = Path(lean_root)
    modules = sorted(set(modules) | {row['module'] for row in rows})
    entries = {name: entry for name, entry in index['entries'].items() if entry['module'] not in modules}
    aux = {name: parent for name, parent in index['aux'].items() if parent is None or parent in entries}
    raw = {row['name']: row for row in rows}
    candidates = [row for row in rows if row['span'] and not row['private'] and not row['internal']
                  and row['kind'] in ENTRY_KINDS]
    new = {}
    for row in candidates:
        inside = any(other['module'] == row['module'] and is_prefix(other['name'], row['name'])
                     and contains(other['span'], row['span']) for other in candidates if other is not row)
        if not inside:
            new[row['name']] = row
    known = set(entries) | set(new)

    def parent(row):
        # Only an entry of the same module: that entry is extracted together with the auxiliary, so
        # what the auxiliary depends on can be made the entry's. An entry elsewhere is not touched.
        parts = name_parts(row['user'])
        for length in range(len(parts) - 1, 0, -1):
            prefix = '.'.join(parts[:length])
            if prefix in new and new[prefix]['module'] == row['module']:
                return prefix
        return None

    for row in rows:
        if row['name'] not in new:
            aux[row['name']] = parent(row)

    def resolve(name, owner, seen, into, axioms, library):
        """Add to `into` the entries that a used canon constant stands for, seen from `owner`."""
        if name in known:
            if name != owner:
                into.add(name)
            return
        target = aux.get(name)
        if target is not None and target != owner:
            into.add(target)
            return
        row = raw.get(name)
        if row is None or name in seen:
            return
        seen.add(name)
        axioms.update(row['axioms'])
        library.update(row['library'])
        for used in row['type_uses'] + row['value_uses']:
            resolve(used, owner, seen, into, axioms, library)

    for name, row in new.items():
        statement_uses, uses = set(), set()
        axioms, library = set(row['axioms']), set(row['library'])
        seen = {name}
        for used in row['type_uses']:
            resolve(used, name, seen, statement_uses, axioms, library)
        for used in row['value_uses']:
            resolve(used, name, seen, uses, axioms, library)
        for child in rows:
            if aux.get(child['name']) == name and child['name'] not in seen:
                resolve(child['name'], name, seen, uses, axioms, library)
        relative = module_file(row['module'])
        text = (lean_root / relative).read_text(encoding='utf-8').replace('\r\n', '\n')
        entries[name] = {
            'name': name, 'kind': row['kind'], 'module': row['module'], 'file': relative, 'span': row['span'],
            'source_sha': sha256_text(declaration_text(text, row['span'])),
            'statement': row['sig'], 'statement_hash': row['statement'], 'prop': bool(row['prop']),
            'statement_uses': sorted(statement_uses), 'uses': sorted(uses - {name}),
            'library': sorted(library), 'direct_axioms': sorted(axioms),
            'lean_proof': None if row['kind'] not in ('theorem', 'def', 'opaque')
            else 'sorry' if 'sorryAx' in axioms else 'complete'}
    table = dict(index['modules'])
    for module in modules:
        relative = module_file(module)
        if (lean_root / relative).is_file():
            table[module] = {'file': relative, 'sha256': hashlib.sha256((lean_root / relative).read_bytes()).hexdigest()}
        else:
            table.pop(module, None)
    return {'revision': revision, 'modules': table, 'entries': entries, 'aux': aux,
            'pairs': {**index.get('pairs', {}), **pairs}}


def drop_modules(index, modules):
    """The index without the entries of modules that no longer exist."""
    modules = set(modules)
    entries = {n: e for n, e in index['entries'].items() if e['module'] not in modules}
    return {**index, 'entries': entries,
            'modules': {m: v for m, v in index['modules'].items() if m not in modules},
            'aux': {n: p for n, p in index['aux'].items() if p is None or p in entries}}


def axiom_closure(index):
    """Every entry's axioms through everything of the canon it uses; a canon axiom counts as itself."""
    entries = index['entries']

    def successors(name):
        entry = entries[name]
        return [used for used in entry['uses'] + entry['statement_uses'] if used in entries]

    # Entries that use one another, directly or in a circle, depend on the same axioms. The components
    # are found in one pass without recursion, each after everything it uses outside itself.
    order, low, closure = {}, {}, {}
    stack, on_stack = [], set()
    for start in entries:
        if start in order:
            continue
        order[start] = low[start] = len(order)
        stack.append(start)
        on_stack.add(start)
        work = [(start, iter(successors(start)))]
        while work:
            name, pending = work[-1]
            for used in pending:
                if used not in order:
                    order[used] = low[used] = len(order)
                    stack.append(used)
                    on_stack.add(used)
                    work.append((used, iter(successors(used))))
                    break
                if used in on_stack:
                    low[name] = min(low[name], order[used])
            else:
                work.pop()
                if work:
                    low[work[-1][0]] = min(low[work[-1][0]], low[name])
                if low[name] == order[name]:
                    component = []
                    while not component or component[-1] != name:
                        component.append(stack.pop())
                        on_stack.discard(component[-1])
                    axioms = set()
                    for member in component:
                        axioms.update(entries[member]['direct_axioms'])
                        if entries[member]['kind'] == 'axiom':
                            axioms.add(member)
                        for used in successors(member):
                            axioms.update(closure.get(used, ()))
                    for member in component:
                        closure[member] = axioms
    return {name: sorted(closure[name]) for name in entries}


def changed_modules(index, lean_root, library):
    """Modules whose source differs from what the index recorded, and modules the index lists that are gone."""
    current = {module: hashlib.sha256(path.read_bytes()).hexdigest()
               for module, path in library_modules(lean_root, library)}
    changed = sorted(m for m, digest in current.items() if index['modules'].get(m, {}).get('sha256') != digest)
    removed = sorted(m for m in index['modules'] if m not in current)
    return changed, removed


# ----------------------------------------------------------------------------- building through the broker

def start_build(instance, lean_root, library, session, expect_mb, extract, pairs, fresh=False, targets=None):
    """Queue one broker build of the library under lean_root, with an extraction of the named modules.

    The extraction file is one more target of the same build, so it is compiled after the modules it
    imports and its output is kept with the build like any target's. Returns the build ID."""
    from lean_broker import Paths, build
    lean_root = Path(lean_root)
    names = [module for module, _ in library_modules(lean_root, library)]
    if not names:
        raise CanonError(f'no module of the library {library} under {lean_root}')
    files = [str(lean_root / module_file(m)) for m in (targets if targets is not None else names)]
    if extract or pairs:
        write_text(lean_root / (EXTRACT_MODULE + '.lean'), extraction_source(library, extract, pairs))
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


def wait_build(instance, build_id, timeout=None, poll=0.5):
    """The outcome of a build, or None when the timeout passes first; the build continues either way.

    A build makes progress only while a broker is alive. Like the broker's own `wait`, this asks for
    one every few seconds, and reports that none came instead of waiting without end."""
    from lean_broker import Paths, ensure_broker
    deadline = None if timeout is None else time.monotonic() + timeout
    checked = time.monotonic()
    while True:
        outcome = build_outcome(instance, build_id)
        if outcome is not None:
            return outcome
        if deadline is not None and time.monotonic() >= deadline:
            return None
        if time.monotonic() - checked > 2.0:
            ensure_broker(Paths(instance))
            checked = time.monotonic()
        time.sleep(poll)


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
        elif (sorted(set(after['uses']) - {item['alternative']}) != sorted(set(before['uses']) - {item['into']})
              or after['lean_proof'] != before['lean_proof']):
            errors.append(f"after retiring {item['alternative']}, the proof of {item['into']} does not name what "
                          'the retired proof named; a retirement moves a proof and does not change it')
    for name in sorted(set(new['entries']) & set(old['entries'])):
        before, after = old['entries'][name], new['entries'][name]
        if before['statement_hash'] != after['statement_hash'] or before['kind'] != after['kind']:
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
            if not (isinstance(record, dict) and record['sections'].get('Proof')):
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
    for name in replaced:
        if name in new['entries'] and name not in records and not existing_record(name):
            errors.append(f'{name} has no record; write records/{name_path(name)}.md')
    closure = axiom_closure(new)
    for name, record in records.items():
        entry = new['entries'][name]
        meta = record['meta']
        for key, kind in (('proves', 'same'), ('refutes', 'negation')):
            target = meta.get(key)
            if not target:
                continue
            if target not in new['entries']:
                errors.append(f'{name}: "{key}: {target}" names no declaration of the canon')
            elif not new.get('pairs', {}).get(f'{kind}|{name}|{target}'):
                errors.append(f'{name}: Lean did not confirm that its statement is '
                              + ('the statement of ' if kind == 'same' else 'the negation of the statement of ') + target)
        if entry['kind'] in STATEMENT_KINDS and entry['lean_proof'] == 'sorry' and not entry['prop']:
            errors.append(f'{name} is a theorem whose statement is not a proposition')
        current = existing_record(name) if name in old['entries'] and name not in replaced else None
        if isinstance(current, dict) and name not in moved.values():
            # Whether an element has a written proof, and what it proves or refutes, decide its standing.
            # Review judges the elements a candidate adds and the proofs it replaces, so a record may
            # change these only for a declaration the candidate lists in "replace".
            same = ((current['sections'].get('Proof') or '').strip() == (record['sections'].get('Proof') or '').strip()
                    and all(current['meta'].get(key) == meta.get(key) for key in ('proves', 'refutes')))
            if not same:
                errors.append(f'{name}: the record changes the written proof, "proves" or "refutes" of an element '
                              'whose proof the candidate does not replace; list the declaration in "replace"')
        if organizer and name in added and entry['kind'] in STATEMENT_KINDS:
            foreign = sorted(set(closure[name]) - set(allowed_axioms))
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
            shutil.copyfile(path, target)
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
    """When an element's proof is accepted, the approaches tried on it go to its history."""
    folder = canon.approaches / name_path(name)
    if folder.is_dir() and any(folder.iterdir()):
        target = canon.history / name_path(name) / f'{revision:06d}-approaches'
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(folder), str(target))
        return True
    return False


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
