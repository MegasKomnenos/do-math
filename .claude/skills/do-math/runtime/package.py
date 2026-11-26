"""What the finalize command does without a session: the scripts of its stages.

Every function here reads files and writes files, and none launches a session or decides the order
of the work; `finalize.py` calls them, and a test can call each alone. They are grouped as the
stages use them: the research as Git has it, the take of step 1, the checks of a library, the lists
of records, the views, the build files and the registry's files of the freeze, the knowledge archive
and the ledger of the history, and the documents with the stand-alone check of the package.
"""
import hashlib
import io
import json
import lzma
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile
import time

import canon
from canon import (BIB_ENTRY, CanonError, IMPORT_LINE, declaration_text, header_scan, library_modules, module_file,
                   name_path, parse_record, path_name, sha256_text, tree_hash)
from command_sessions import read_file as read_text
from runtime_support import popen_options, read_json, write_text as write_file

MAX_LINES = 10_000       # physical lines of a Lean file, the registry's rule and the canon's
CHALLENGE_LINES = 1_000   # the registry's limits on Challenge.lean
CHALLENGE_BYTES = 100 * 1024
CHALLENGE_IMPORTS = ('Init', 'Lean', 'Std', 'Mathlib')
COMPARATOR_REQUIRED = ('challenge_module', 'solution_module', 'theorem_names', 'permitted_axioms')
COMPARATOR_OPTIONAL = ('definition_names', 'enable_nanoda')
PERMITTED_AXIOMS = ['propext', 'Quot.sound', 'Classical.choice']
RELATIONSHIPS = ('formalizes', 'adapts', 'independently-proves', 'background', 'other')
RELATED = ('builds-on', 'adapts', 'independent', 'supersedes', 'other')  # this library and an earlier formalisation
ARXIV = re.compile(r'[a-z][a-z-]*(\.[A-Za-z][A-Za-z-]*)?')
MSC = re.compile(r'\d\d[A-Z-]([0-9]{2}|[xX]{2})')
ACCOUNT = '<account>'
WRITER_BATCH = 40   # records one writer or comparer takes
HISTORY_BATCH = 12  # events one history writer takes
MODIFIERS = ('private', 'protected', 'public', 'noncomputable', 'unsafe', 'partial', 'nonrec', 'meta', 'scoped', 'local')
ATTRIBUTE_COMMAND = re.compile(r'^\s*attribute\s*\[[^\]]*\]\s+([^\n]*)$', re.M)
BACKTICKED = re.compile(r'`([^`\n]+)`')
DRIVE_PATH = re.compile(r'(?<![A-Za-z])[A-Za-z]:[\\/](?![\\/])')
# In Markdown, TeX and BibTeX a backslash after a colon begins a command of a formula, as in $f:\mathbb{N}\to X$,
# so a drive path is looked for there in its form with a slash, which is the form a session is given paths in.
DRIVE_PATH_IN_MARKUP = re.compile(r'(?<![A-Za-z])[A-Za-z]:/(?!/)')
LINK = re.compile(r'\]\(([^)\s]+)(?:\s+"[^"]*")?\)|(?:href|src)\s*=\s*"([^"]*)"')
# Lean prints the name between apostrophes, and a name can hold one itself, as `step'` does: the apostrophe that
# closes the name is the one that a space follows.
AXIOM_LINE = re.compile(r"'((?:[^'\n]|'(?=[^ \n]))+)' (?:depends on axioms: \[(.*?)\]|does not depend on any axioms)", re.S)


def write_text(path, content):
    """Write a complete UTF-8 file, with its folder, by writing beside it and replacing it.

    Every line of the file ends with a line feed alone: a text that came with Windows line endings,
    from a file or from a value of a session's JSON, is written without their carriage returns.
    The file is written and put in place by the runtime's writer (runtime_support.write_text)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_file(path, content.replace('\r\n', '\n'))


def write_json(path, value):
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def product_hash(path):
    """The identity of a product: the SHA-256 of a file, `canon.tree_hash` of a folder."""
    path = Path(path)
    return tree_hash(path) if path.is_dir() else sha256_file(path)


def files_under(root):
    """The files of a folder by their relative /-separated path."""
    root = Path(root)
    return {path.relative_to(root).as_posix(): path for path in sorted(root.rglob('*')) if path.is_file()} \
        if root.is_dir() else {}


# ----------------------------------------------------------------------------- the research as Git has it

def git_run(repository, *arguments):
    """The output of a Git command in a repository, as bytes; an error says what Git said."""
    environment = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    done = subprocess.run(['git', '-C', str(repository), '-c', 'core.autocrlf=false', '-c', 'core.quotepath=false',
                           *arguments], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment,
                          **popen_options())
    if done.returncode:
        raise CanonError('Git: ' + done.stderr.decode('utf-8', errors='replace').strip())
    return done.stdout


def head_commit(repository):
    return git_run(repository, 'rev-parse', 'HEAD').decode().strip()


def first_commit(repository, commit):
    return git_run(repository, 'rev-list', '--max-parents=0', commit).decode().split()[-1]


def commit_time(repository, commit):
    return int(git_run(repository, 'show', '-s', '--format=%ct', commit).decode().strip())


def git_members(repository, commit, paths):
    """The regular files of a commit under the given paths, as (path, bytes), from `git archive`.

    The files come as Git stores them: `core.autocrlf` is off for the command, so no line ending is
    converted on the way out."""
    environment = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    process = subprocess.Popen(['git', '-C', str(repository), '-c', 'core.autocrlf=false', 'archive', '--format=tar',
                                commit, '--', *paths], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment,
                               **popen_options())
    try:
        with tarfile.open(fileobj=process.stdout, mode='r|') as stream:
            for member in stream:
                if member.isreg():
                    yield member.name, stream.extractfile(member).read()
    except tarfile.ReadError:
        pass  # Git wrote no archive; its exit code and message say why
    finally:
        process.stdout.read()  # the padding after the last member: Git fails when its output is closed before the end
        process.stdout.close()
        message = process.stderr.read().decode('utf-8', errors='replace').strip()
        process.stderr.close()
        if process.wait():
            raise CanonError('Git: ' + message)


def export_commit(repository, commit, paths, target, strip=''):
    """Write the files of a commit under the given paths into a folder; `strip` is a path prefix to leave out."""
    target = Path(target)
    for name, data in git_members(repository, commit, paths):
        relative = name[len(strip):] if strip and name.startswith(strip) else name
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def reduced_settings(settings):
    """The instance's settings with the Lean block reduced to what names the Lean environment.

    The operating values of an instance (budgets, the free memory it insists on) would stop this
    run or slow it, so they take their defaults here; the cache key of a module depends on none of them."""
    kept = ('command', 'version_command', 'cwd', 'env', 'cache_epoch', 'allowed_axioms')
    return {**settings, 'lean': {key: settings['lean'][key] for key in kept if key in settings['lean']}}


# ----------------------------------------------------------------------------- modules

def local_imports(lean_root, library):
    """For each module of the library, the modules of the library it imports directly."""
    modules = dict(library_modules(lean_root, library))
    return {name: [i for i in header_scan(read_text(path).split('\n'))[2] if i in modules]
            for name, path in modules.items()}


def import_closure(imports, modules):
    """The named modules and everything they import, directly or through one another."""
    reached, pending = set(), list(modules)
    while pending:
        module = pending.pop()
        if module not in reached and module in imports:
            reached.add(module)
            pending += imports[module]
    return reached


def import_order(imports, modules):
    """The named modules so that each comes after the modules it imports; ties by name."""
    ordered, seen = [], set()

    def visit(module):
        if module in seen:
            return
        seen.add(module)
        for imported in sorted(imports.get(module, ())):
            if imported in modules:
                visit(imported)
        ordered.append(module)

    for module in sorted(modules):
        visit(module)
    return ordered


def definition_modules(first_lean, library, root_module):
    """The modules the root's module imported in the first commit, directly or through one another, in import order."""
    imports = local_imports(first_lean, library)
    if root_module not in imports:
        raise CanonError(f'the first commit has no module {root_module}')
    return import_order(imports, import_closure(imports, imports[root_module]))


# ----------------------------------------------------------------------------- step 1: the take

def carries_attribute(text):
    """Whether a declaration's source carries an attribute or is an instance.

    Lean uses such a declaration without naming it in a proof term: a `simp` lemma, an instance, an
    `ext` lemma. The text is the declaration as its span gives it, doc comment and modifiers included."""
    rest = text.lstrip()
    if rest.startswith('/--'):
        rest = rest[rest.find('-/') + 2:].lstrip()
    if rest.startswith('@['):
        return True
    for word in re.findall(r"[A-Za-z_][A-Za-z_0-9']*", rest[:400]):
        if word not in MODIFIERS:
            return word == 'instance'
    return False


def attribute_named(texts):
    """The names that an `attribute [...] names` command gives an attribute to, as they are written."""
    names = set()
    for text in texts:
        for found in ATTRIBUTE_COMMAND.findall(text):
            for word in found.split():
                if word == 'in':
                    break
                names.add(word)
    return names


def without_elements(text, spans):
    """A source text less the declarations at the given spans, each removed as a whole.

    A line that the removal leaves empty goes with it, and where two blank lines then meet one of
    them goes, so that the file reads as it would had the declaration never stood there."""
    lines = text.split('\n')
    for first, start, last, end in sorted((list(span) for span in spans), reverse=True):
        merged = lines[first - 1][:start] + lines[last - 1][end:]
        lines[first - 1:last] = [merged] if merged.strip() else []
        at = first - 1
        if not merged.strip() and 0 < at < len(lines) and not lines[at - 1].strip() and not lines[at].strip():
            del lines[at]
    return '\n'.join(lines)


def take(index, lean_root, library, root, definitions, allowed):
    """What step 1 keeps of a library and what it removes; nothing is written.

    Kept are the elements reached from the root through `uses` and `statement_uses`, every element of
    a definition module, every element that carries an attribute or is an instance, and what any of
    these reach. A declaration that is no element stays in its file, so the elements such a
    declaration names are kept as well (the index holds them under `hidden`). Every other element is
    removed as a whole, by its span.

    `allowed` are the axioms the instance allows. One kind of element is never kept for its attribute
    or because a declaration that is no element names it: a theorem that is not proved from those
    axioms. A finished research holds such theorems beside the proof of its root, and the frozen
    library has to be proved throughout; what the root reaches is proved, since the root is. When a
    file then no longer compiles, the build of step 1 says so. A module stays when it holds a kept element, is a definition
    module or the root's module, or is imported by a module that stays; every other module is deleted.

    Returns `kept` and `removed` (names), `spans` (for each removed element its file and span),
    `modules` and `deleted` (module names), and `files`: the text of every file that stays."""
    lean_root = Path(lean_root)
    entries = index['entries']
    if root not in entries:
        raise CanonError(f'the root {root} is not in the index')
    modules = dict(library_modules(lean_root, library))
    texts = {module_file(name): read_text(path) for name, path in modules.items()}
    named = attribute_named(texts.values())
    seeds = {root}
    open_ = {name for name, entry in entries.items() if entry['kind'] == 'theorem'
             and entry['module'] not in definitions and canon.beyond_allowed(entry, allowed)}
    for name, entry in entries.items():
        if entry['file'] not in texts:
            raise CanonError(f"the index names {entry['file']} for {name}, and the library has no such file")
        source = declaration_text(texts[entry['file']], entry['span'])
        if sha256_text(source) != entry['source_sha']:
            raise CanonError(f'the source of {name} is not the text the index was extracted from')
        if name not in open_ and (
                entry['module'] in definitions or carries_attribute(source) or name in named
                or name.rsplit('.', 1)[-1] in named or any(name.endswith('.' + word) for word in named)):
            seeds.add(name)
    imports = local_imports(lean_root, library)
    hidden = index.get('hidden', {})
    kept, staying = set(), set()
    while True:
        for name in seeds:
            if name not in kept:
                kept |= rests_from(index, name)
        holders = {entries[name]['module'] for name in kept} | set(definitions) | {entries[root]['module']}
        staying = import_closure(imports, holders)
        # What a declaration that is no element names stays with it.
        more = {used for item in hidden.values() if item['module'] in staying for used in item['uses']
                if used in entries} - kept - open_
        if not more:
            break
        seeds |= more
    removed = sorted(set(entries) - kept)
    spans = [{'declaration': name, 'file': entries[name]['file'], 'span': entries[name]['span']}
             for name in removed if entries[name]['module'] in staying]
    files = {}
    for module in sorted(staying):
        relative = module_file(module)
        cut = [item['span'] for item in spans if item['file'] == relative]
        files[relative] = without_elements(texts[relative], cut) if cut else texts[relative]
    return {'kept': sorted(kept), 'removed': removed, 'spans': spans, 'modules': sorted(staying),
            'deleted': sorted(set(modules) - staying), 'files': files}


def restored_files(spans, before, returned):
    """What a restore session put back, and the problems of its output.

    `spans` are the removed elements of the files that stay, `before` the text of each file before the
    take, `returned` the files the session wrote, by path under `lean/`. A removed element counts as
    put back when its whole source stands in the returned file. The file the script then writes is
    its own: the file before the take less the elements that stay removed. The returned file has to
    be that file apart from blank lines and trailing spaces, since a restore session puts removed
    elements back and does nothing else. Returns (names put back, files to write, problems)."""
    squeezed = lambda text: [line.rstrip() for line in text.replace('\r\n', '\n').split('\n') if line.strip()]
    back, files, problems = [], {}, []
    for relative, text in returned.items():
        if relative not in before:
            problems.append(f'lean/{relative} is no file of the taken library; a removed element is put back in the '
                            'file it stood in')
            continue
        text = text.replace('\r\n', '\n')
        here = [item for item in spans if item['file'] == relative]
        again = [item for item in here if declaration_text(before[relative], item['span']).strip() in text]
        expected = without_elements(before[relative], [item['span'] for item in here if item not in again])
        if squeezed(expected) != squeezed(text):
            problems.append(f'lean/{relative} differs from the file before the take by more than removed elements put '
                            'back whole; put a removed element back exactly as it stood, and change nothing else')
            continue
        back += [item['declaration'] for item in again]
        files[relative] = expected
    return sorted(back), files, problems


# ----------------------------------------------------------------------------- the checks of a library

def lean_form_problems(lean_root, lean_only=True):
    """Every `.lean` file begins with `module` after its comments and has at most 10,000 physical lines.

    A module root holds .lean files only, so any other file there is a problem. Without `lean_only` the
    folder is a Lake project, which holds other files too: they and Lake's own folder are passed over."""
    problems = []
    for relative, path in files_under(lean_root).items():
        if not relative.endswith('.lean'):
            if lean_only:
                problems.append(f'{relative} is no Lean file; a module root holds .lean files only')
            continue
        if not lean_only and relative.startswith('.lake/'):
            continue
        lines = read_text(path).split('\n')
        if not header_scan(lines)[1]:
            problems.append(f'{relative} does not begin with `module`')
        count = len(lines) - (1 if lines and lines[-1] == '' else 0)
        if count > MAX_LINES:
            problems.append(f'{relative} has {count} lines; a Lean file has at most {MAX_LINES}')
    return problems


def definition_problems(lean_root, first_lean, definitions):
    """Each definition module has the bytes it has in the first commit."""
    problems = []
    for module in definitions:
        now, first = Path(lean_root) / module_file(module), Path(first_lean) / module_file(module)
        if not now.is_file():
            problems.append(f'the definition module {module} is missing')
        elif sha256_file(now) != sha256_file(first):
            problems.append(f'the definition module {module} is not the file of the first commit')
    return problems


def read_records(records_root):
    """The records under a folder by the name path of their file, each parsed or as the error it gives."""
    found = {}
    for relative, path in files_under(records_root).items():
        if relative.endswith('.md'):
            try:
                found[relative[:-3]] = parse_record(path.read_text(encoding='utf-8-sig'), 'records/' + relative)
            except CanonError as error:
                found[relative[:-3]] = error
    return found


def index_problems(index, root, statement_hash, allowed, records=None):
    """The checks of a library that read its index.

    The root is a theorem with the statement the instance fixed; every theorem has a complete proof
    from the allowed axioms, and no declaration that is no element has an open proof; no two names
    differ only in case; and `canon.check_applied` reports
    nothing. With `records` (by name path) the records are due: every element has one, every record
    has an element, and what a record claims to prove or refute Lean confirmed. Without, the same
    check runs with an empty record for every element, so that it reports what does not concern records."""
    entries = index['entries']
    problems = []
    entry = entries.get(root)
    if entry is None or entry['kind'] != 'theorem':
        problems.append(f'the root {root} is not a theorem of the library')
    elif entry['statement_hash'] != statement_hash:
        problems.append(f'the statement of the root {root} is not the statement the instance fixed')
    for name, item in sorted(entries.items()):
        if item['kind'] == 'theorem':
            foreign = canon.beyond_allowed(item, allowed)
            if foreign:
                problems.append(f'{name} is not proved from the allowed axioms: ' + ', '.join(foreign))
    # A declaration that is no element, such as a private lemma, stays in its file through every step. Where no
    # element uses it, no element's list of axioms shows that its proof is open, so the index is asked for it.
    opened = {item.get('user') or name for name, item in index.get('hidden', {}).items() if item.get('sorry')}
    problems += [f'{name}, a declaration that is no element, has an open proof (`sorry`)' for name in sorted(opened)]
    for group in canon.case_collisions(entries):
        problems.append('the names ' + ', '.join(group) + ' differ only in the case of their letters')
    if records is None:
        given = {name_path(name): {'meta': {}, 'sections': {}} for name in entries}
    else:
        problems += [str(record) for record in records.values() if isinstance(record, CanonError)]
        given = {path: record for path, record in records.items() if not isinstance(record, CanonError)}
    problems += canon.check_applied(canon.empty_index(), index, {'replace': [], 'retire': []}, given,
                                    lambda name: False, allowed)['errors']
    return problems


# ----------------------------------------------------------------------------- views

def make_view(view, lean_root, records_root, bibliography, index, source, settings, account):
    """A folder that `knowledge.replay`, `depmap.py` and `paper.py` read as an instance: a library and no history.

    `source` is the research at the pinned commit, from which the root in words and `instance.json`
    come; `account` is the account of the chosen proof, which stands as the understanding of the root
    question in place of the research's own."""
    import knowledge
    view, source = Path(view), Path(source)
    (view / 'canon' / 'questions').mkdir(parents=True)
    shutil.copytree(lean_root, view / 'canon' / 'lean')
    shutil.copytree(records_root, view / 'canon' / 'records')
    if Path(bibliography).is_file():
        shutil.copyfile(bibliography, view / 'canon' / 'bibliography.bib')
    write_json(view / 'canon' / 'index.json', index)
    shutil.copyfile(source / 'root.md', view / 'root.md')
    write_json(view / 'instance.json', read_json(source / 'instance.json'))
    write_json(view / 'settings.json', settings)
    write_text(view / 'canon' / 'questions' / 'q0.md', account.strip() + '\n')
    write_json(view / 'canon' / 'records.json', knowledge.record_summary(view, index))
    return view


# ----------------------------------------------------------------------------- records

def record_todo(index, base, records_root):
    """The elements whose record is to be written, in the form of `todo.json`.

    Those without a record; those whose declaration is not in the base index with the same source;
    and those whose record names a declaration the base index had and the library no longer has:
    between backticks, by its full name or by its name without the library's first component, or
    after `proves:` or `refutes:`, as the declaration it claims to prove or to refute. The check of
    the records refuses a claim about a declaration that is gone, so the record that makes it is due.
    So is a record whose claim under `proves` or `refutes` Lean did not confirm when `index` was
    extracted, as after a rename of the declaration it names: the check requires every such claim to
    be confirmed, and only a session changes a record."""
    records_root = Path(records_root)
    confirmed = index.get('pairs', {})

    def unconfirmed(name, text):
        try:
            meta = parse_record(text, name)['meta']
        except CanonError:
            return False  # the check of the records reports a record that does not parse
        return any(meta.get(key) and not confirmed.get(f'{kind}|{name}|{meta[key]}')
                   for key, kind in (('proves', 'same'), ('refutes', 'negation')))

    gone = set(base['entries']) - set(index['entries'])
    short = lambda name: name.split('.', 1)[1] if '.' in name else name
    standing = {short(name) for name in index['entries']}
    names = gone | {short(name) for name in gone if short(name) not in standing}
    todo = []
    for name, entry in sorted(index['entries'].items()):
        relative = 'records/' + name_path(name) + '.md'
        path = records_root / (name_path(name) + '.md')
        old = base['entries'].get(name)
        if not path.is_file():
            why = 'new'
        elif old is None or old['source_sha'] != entry['source_sha']:
            why = 'changed'
        elif (set(BACKTICKED.findall(text := read_text(path)))
              | set(re.findall(r'^(?:proves|refutes):[ \t]*(\S+)[ \t]*$', text, re.M))) & names:
            why = 'names a declaration that is gone'
        elif unconfirmed(name, text):
            why = 'claims what Lean did not confirm'
        else:
            continue
        todo.append({'declaration': name, 'file': entry['file'], 'why': why, 'record': relative if path.is_file() else None})
    return todo


def batches(items, size, key=lambda item: ''):
    """Items in groups of at most `size`, each group from one key (a folder of modules); with their numbers."""
    groups = {}
    for item in items:
        groups.setdefault(key(item), []).append(item)
    found = []
    for name in sorted(groups):
        for start in range(0, len(groups[name]), size):
            found.append(groups[name][start:start + size])
    return [(f'{number:02d}', group) for number, group in enumerate(found, 1)]


def with_new_names(text, renames):
    """A text in which every renamed declaration that stands between backticks has its new name."""
    return BACKTICKED.sub(lambda match: '`' + renames.get(match[1], match[1]) + '`', text)


def follow_renames(records_root, renames, removed):
    """Bring the records to a table of renamed declarations and a list of removed ones.

    A record goes to the path of its declaration's new name. Inside every record, a renamed name that
    stands between backticks or after `proves:` or `refutes:` is replaced by the new one. The record of
    a removed declaration is deleted."""
    records_root = Path(records_root)
    for name in removed:
        (records_root / (name_path(name) + '.md')).unlink(missing_ok=True)
    moved = {}
    for old, new in renames.items():
        path = records_root / (name_path(old) + '.md')
        if path.is_file():
            moved[new] = path.read_text(encoding='utf-8-sig')
            path.unlink()
    for new, text in moved.items():
        write_text(records_root / (name_path(new) + '.md'), text.replace('\r\n', '\n'))
    if renames:
        header = lambda match: match[1] + renames.get(match[2], match[2])
        for path in files_under(records_root).values():
            text = read_text(path)
            changed = re.sub(r'^((?:proves|refutes):\s*)(\S+)[ \t]*$', header, with_new_names(text, renames), flags=re.M)
            if changed != text:
                write_text(path, changed)
    for folder in sorted((p for p in records_root.rglob('*') if p.is_dir()), reverse=True):
        if not any(folder.iterdir()):
            folder.rmdir()


def drop_orphans(records_root, index):
    """Delete the records whose declaration the library no longer has; returns their names."""
    paths = {name_path(name) for name in index['entries']}
    gone = []
    for relative, path in files_under(records_root).items():
        if relative.endswith('.md') and relative[:-3] not in paths:
            path.unlink()
            gone.append(path_name(relative[:-3]))
    return gone


CITATION = re.compile(r'\[([A-Za-z0-9][A-Za-z0-9_.+:-]*)(?:\s*,[^\]\n]*)?\]')


def citations(text, keys):
    """The citations in a record's text, as written, each with its key: `[key]` or `[key, place]` for a key of `keys`.

    The records cite a work by its key in the bibliography between square brackets, alone or followed
    by a comma and the place in the work. The keys tell such a citation from other text in brackets."""
    return [(match[1], match[0]) for match in CITATION.finditer(text) if match[1] in keys]


def cited_in(texts, keys):
    """For every bibliography key that a record cites, the records that cite it; `texts` maps a declaration to its record.

    A record cites a work in two ways: its header names the key as the source of the result, and its
    text has a citation of the key (citations), where `keys` are the keys of the bibliography. Each
    record is given with its path, its text, whether its header names the key ("header") and its
    citations of the key as they are written ("citations")."""
    found = {}
    for name in sorted(texts):
        text = texts[name]
        try:
            source = parse_record(text, name)['meta'].get('source')
        except CanonError:
            continue
        written = {}
        for key, citation in citations(text, keys):
            written.setdefault(key, []).append(citation)
        for key in sorted(set(written) | ({source} if source else set())):
            found.setdefault(key, []).append({'declaration': name, 'path': 'records/' + name_path(name) + '.md',
                                              'text': text, 'header': key == source,
                                              'citations': list(dict.fromkeys(written.get(key, [])))})
    return [{'key': key, 'records': records} for key, records in sorted(found.items())]


def cited(records_root, index, keys):
    """`cited.json`: for every bibliography key that a record of the library cites, the records that cite it (cited_in)."""
    texts = {}
    for name in index['entries']:
        path = Path(records_root) / (name_path(name) + '.md')
        if path.is_file():
            texts[name] = read_text(path)
    return cited_in(texts, keys)


def bibliography_keys(text):
    return set(BIB_ENTRY.findall(text))


def bibliography_field(text, key, field):
    """One field of one entry of a BibTeX file, without its braces; empty when it is not there."""
    entry = re.search(r'@\w+\s*\{\s*' + re.escape(key) + r'\s*,(.*?)(?=^@|\Z)', text, re.S | re.M)
    if not entry:
        return ''
    found = re.search(r'\b' + field + r'\s*=\s*(\{|")', entry[1], re.I)
    if not found:
        return ''
    start, depth, out = found.end(), 1, []
    closing = '}' if found[1] == '{' else '"'
    for char in entry[1][start:]:
        if found[1] == '{' and char == '{':
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                break
        out.append(char)
    return ' '.join(''.join(out).replace('{', '').replace('}', '').split())


# ----------------------------------------------------------------------------- parts

def interface(index, modules, fixed=()):
    """The declarations of a set of modules that keep their names and statements, with their statements.

    They are the declarations that elements of other modules use, and those of `fixed` that lie in these
    modules: the root and the main theorem, which every later step of a run finds by name."""
    modules = set(modules)
    used = set(fixed)
    for entry in index['entries'].values():
        if entry['module'] not in modules:
            used.update(entry['uses'] + entry['statement_uses'])
    return [{'declaration': name, 'statement': index['entries'][name]['statement']}
            for name in sorted(used) if name in index['entries'] and index['entries'][name]['module'] in modules]


def part_output(output, base_lean, owns, definitions, may_add=lambda module: True):
    """What a simplifying or folding session returned for its part, and the problems of it.

    `owns(module)` says whether a module of the library is the part's to change, `may_add(module)`
    whether a module the library does not have yet may enter with this part. A returned file is one or
    the other; a deleted file is a module the part owns; a definition module is neither.
    Returns (files by path under lean/, deleted paths, problems)."""
    output, base_lean = Path(output), Path(base_lean)
    files = {relative: read_text(path) for relative, path in files_under(output / 'lean').items()}
    report = output / 'report.json'
    deleted = read_json(report).get('deleted', []) if report.is_file() else []
    problems = []
    if not isinstance(deleted, list) or not all(isinstance(item, str) for item in deleted):
        return files, [], ['"deleted" in report.json is an array of paths under lean/']
    deleted = [item[len('lean/'):] if item.startswith('lean/') else item for item in deleted]
    for relative in list(files) + deleted:
        module = '.'.join(PurePosixPath(relative).with_suffix('').parts)
        if not relative.endswith('.lean'):
            problems.append(f'lean/{relative} is no Lean file')
        elif module in definitions:
            problems.append(f'{module} is a definition module, which no part changes')
        elif (base_lean / relative).is_file() or relative in deleted:
            if not owns(module):
                problems.append(f'{module} is not a module of this part')
            elif relative in deleted and not (base_lean / relative).is_file():
                problems.append(f'lean/{relative} is listed as deleted and the library has no such file')
        elif not may_add(module):
            problems.append(f'the new module {module} does not lie in this part')
    return files, deleted, problems


# ----------------------------------------------------------------------------- what a session is given, as text

def rests_from(index, name):
    """Every element reached from one through `uses` and `statement_uses`, itself included."""
    entries = index['entries']
    reached, pending = set(), [name]
    while pending:
        current = pending.pop()
        if current in reached or current not in entries:
            continue
        reached.add(current)
        pending += entries[current]['uses'] + entries[current]['statement_uses']
    return reached


def lines_of(entry):
    return entry['span'][2] - entry['span'][0] + 1


def selection_digest(model, index):
    """`digest.md` of the selection: the proofs that settle the root, and the settled units they do not rest on."""
    import knowledge
    elements, entries = model['elements'], index['entries']
    root = model['root']
    settlement = knowledge.root_settlement(model) or {'proofs': []}
    lines = ['# Digest of the canon for the selection', '',
             f'The root is `{root}`: `{entries[root]["statement"]}`.', '',
             '## Declarations whose proof formally settles the root', '']
    under = set()
    for proof in settlement['proofs']:
        reached = rests_from(index, proof)
        under |= reached
        modules = sorted({entries[name]['module'] for name in reached})
        lines += [f'### `{proof}`', '',
                  f'It rests on {len(reached)} elements in {len(modules)} modules, '
                  f'{sum(lines_of(entries[name]) for name in reached)} lines of declarations.', '',
                  'Modules: ' + ', '.join(f'`{module}`' for module in modules) + '.', '', 'The units among them:', '']
        lines += [f"- `{name}`: {elements[name]['description']}" for name in sorted(reached)
                  if elements[name]['weight'] == 'unit']
        lines.append('')
    lines += ['## Settled formal theorems of weight unit that these proofs do not rest on', '']
    others = [name for name, element in sorted(elements.items())
              if element['kind'] == 'theorem' and element['weight'] == 'unit' and element['settled']
              and element['formal'] and name not in under]
    for name in others:
        lines += [f'### `{name}`', '', '```lean', entries[name]['statement'], '```', '', elements[name]['description'], '']
    if not others:
        lines += ['None.', '']
    return '\n'.join(lines)


def rests_on_text(index, kept=None):
    """`rests-on.md`: for each element, what its statement names and what its proof names."""
    lines = ['# What rests on what', '']
    for name, entry in sorted(index['entries'].items()):
        if kept is not None and name not in kept:
            continue
        lines.append(f"- `{name}` ({entry['kind']}, `{entry['module']}`): statement names "
                     + (', '.join(f'`{used}`' for used in entry['statement_uses']) or 'nothing') + '; proof names '
                     + (', '.join(f'`{used}`' for used in entry['uses']) or 'nothing'))
    return '\n'.join(lines) + '\n'


def declarations_text(index):
    """`declarations.md`: every element of a library by module, with its statement."""
    lines, module = ['# The declarations of the library'], None
    for name, entry in sorted(index['entries'].items(), key=lambda item: (item[1]['module'], item[1]['span'])):
        if entry['module'] != module:
            module = entry['module']
            lines += ['', f'## `{module}`', '']
        lines.append(f"- {entry['kind']} `{entry['statement']}`")
    return '\n'.join(lines) + '\n'


# ----------------------------------------------------------------------------- the freeze: build files

def lake_command(settings):
    """The `lake` program of the Lean environment: the first word of `lake env lean`, or the one beside Lean."""
    command = settings['lean']['command']
    if len(command) >= 3 and command[1:3] == ['env', 'lean']:
        return [command[0]]
    lean = Path(shutil.which(command[0]) or command[0])
    return [str(lean.with_name('lake' + lean.suffix))]


def lake_project(settings):
    """The Lake project that the settings name as `lean.cwd`, or None when they name none."""
    folder = settings['lean'].get('cwd')
    return Path(folder) if folder and (Path(folder) / 'lake-manifest.json').is_file() else None


def toolchain_of(version):
    """The toolchain name for the version string Lean reports."""
    found = re.search(r'version (\d+\.\d+\.\d+(?:-[A-Za-z0-9.]+)?)', version or '')
    if not found:
        raise CanonError(f'the Lean version cannot be read from what Lean reports: {version!r}')
    return 'leanprover/lean4:v' + found[1]


def release_of(toolchain):
    """`Lean 4.36.0` for the toolchain `leanprover/lean4:v4.36.0`: the release as a sentence names it."""
    version = toolchain.rpartition(':')[2]
    return 'Lean ' + (version[1:] if version[:1] == 'v' and version[1:2].isdigit() else version)


def build_files(library, name, project, version, top_module):
    """`lean-toolchain`, `lakefile.toml` and `lake-manifest.json` of the published layout.

    The toolchain, the `[[require]]` blocks and the packages are those of the Lake project the Lean
    environment runs in; without one, the toolchain is the version Lean reports and nothing is required."""
    package = re.sub(r'[^a-z0-9_]', '_', name.lower())
    requires, packages = [], []
    if project is not None:
        toolchain = read_text(project / 'lean-toolchain').strip()
        lakefile = project / 'lakefile.toml'
        if not lakefile.is_file():
            raise CanonError(f'{project} declares its dependencies in lakefile.lean; the build files of the package are '
                             'taken from a lakefile.toml')
        requires = re.findall(r'^\[\[require\]\]\n(?:(?!\[).*\n?)*', read_text(lakefile), re.M)
        packages = read_json(project / 'lake-manifest.json')['packages']
    else:
        toolchain = toolchain_of(version)
    blocks = [f'name = "{package}"\ndefaultTargets = ["{library}", "Challenge", "Solution"]\n']
    blocks += [block.strip() + '\n' for block in requires]
    blocks.append(f'[[lean_lib]]\nname = "{library}"\nglobs = ["{library}.{"*" if top_module else "+"}"]\n')
    blocks += [f'[[lean_lib]]\nname = "{target}"\nroots = ["{target}"]\n' for target in ('Challenge', 'Solution')]
    manifest = {'version': '1.3.0', 'packagesDir': '.lake/packages', 'packages': packages, 'name': package,
                'lakeDir': '.lake'}
    return {'lean-toolchain': toolchain + '\n', 'lakefile.toml': '\n'.join(blocks),
            'lake-manifest.json': json.dumps(manifest, indent=1) + '\n'}


def packages_problems(manifest, packages_dir):
    """Every Git package of a manifest stands in the packages folder at the manifest's revision."""
    problems = []
    for package in manifest['packages']:
        if package.get('type') != 'git':
            continue
        folder = Path(packages_dir) / package['name']
        try:
            head = git_run(folder, 'rev-parse', 'HEAD').decode().strip() if folder.is_dir() else None
        except CanonError:
            head = None
        if head != package['rev']:
            problems.append(f"the package {package['name']} is not at {package['rev'][:12]} in {packages_dir} "
                            f"(found: {head[:12] if head else 'nothing'}); Lake would fetch it from the network")
    return problems


def lake_run(lake, folder, *arguments, env=None):
    """Run Lake in a project folder; returns (exit code, standard output, standard error).

    `env` holds the variables of `lean.env`, with which the Lean environment is run. They are added to those of
    this process, as the version command of the run and its broker add them."""
    try:
        done = subprocess.run([*lake, *arguments], cwd=folder, env={**os.environ, **(env or {})},
                              stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              **popen_options())
    except OSError as error:
        return None, '', str(error)
    decode = lambda data: data.decode('utf-8', errors='replace').replace('\r\n', '\n')
    return done.returncode, decode(done.stdout), decode(done.stderr)


def axioms_printed(output):
    """What `#print axioms` lines say: for each name the axioms it depends on."""
    return {name: [axiom.strip() for axiom in (listed or '').split(',') if axiom.strip()]
            for name, listed in AXIOM_LINE.findall(output)}


# ----------------------------------------------------------------------------- the freeze: the registry's files

def challenge_text(first_lean, definitions, root_module, main_statement=None):
    """`Challenge.lean`: the definition modules and the root's module of the first commit joined into one module.

    One header with their imports from outside the library, then their bodies in import order. The
    root stands there as it was posed, its proof left open. With `main_statement`, the statement of
    the main theorem as the index prints it follows, its proof left open as well."""
    local = set(definitions) | {root_module}
    externals, bodies = [], []
    for module in [*definitions, root_module]:
        lines = read_text(Path(first_lean) / module_file(module)).split('\n')
        end = header_scan(lines)[0]
        for line in lines[:end]:
            found = IMPORT_LINE.match(line.strip())
            if found and found[2] not in local and line.strip() not in externals:
                externals.append(line.strip())
        bodies.append('\n'.join(lines[end:]).strip('\n'))
    text = 'module\n\n' + ('\n'.join(externals) + '\n\n' if externals else '') + '\n\n'.join(bodies) + '\n'
    if main_statement:
        text += '\ntheorem ' + main_statement + ' := by\n  sorry\n'
    return text


def challenge_measure(text):
    """The registry's rules on Challenge.lean that the research may be unable to meet, measured on a text."""
    lines = text.split('\n')
    count = len(lines) - (1 if lines[-1] == '' else 0)
    size = len(text.encode('utf-8'))
    imports = header_scan(lines)[2]
    fails = []
    if count > CHALLENGE_LINES:
        fails.append(f'Challenge.lean has {count} lines; the registry accepts at most {CHALLENGE_LINES}')
    if size > CHALLENGE_BYTES:
        fails.append(f'Challenge.lean has {size} bytes; the registry accepts at most {CHALLENGE_BYTES}')
    foreign = [name for name in imports if name.split('.')[0] not in CHALLENGE_IMPORTS]
    if foreign:
        fails.append('Challenge.lean imports ' + ', '.join(foreign) + '; the registry accepts imports of Lean and of '
                     'the pinned Mathlib only')
    return {'lines': count, 'bytes': size, 'imports': imports, 'fails': fails}


def solution_text(modules):
    """`Solution.lean`: a module that imports the library's modules of the compared theorems, and nothing else."""
    return 'module\n\n' + ''.join(f'public import {module}\n' for module in dict.fromkeys(modules))


def comparator(theorems):
    return {'challenge_module': 'Challenge', 'solution_module': 'Solution', 'theorem_names': list(theorems),
            'permitted_axioms': list(PERMITTED_AXIOMS)}


def check_text(root_module, names):
    """`Check.lean`: prints the statements of the named theorems and the axioms they depend on."""
    lines = ['module', '', f'import {root_module}', '',
             '/-! After `lake build`, `lake env lean Check.lean` prints the statements and the axioms they rest on. -/', '']
    for name in dict.fromkeys(names):
        lines += [f'#check @{name}', f'#print axioms {name}']
    return '\n'.join(lines) + '\n'


def yaml_text(value, indent=0):
    """A value of dictionaries, lists, strings, numbers and booleans as YAML; every string is double-quoted."""
    pad = '  ' * indent

    def scalar(item):
        if isinstance(item, bool):
            return 'true' if item else 'false'
        if isinstance(item, (int, float)):
            return str(item)
        if isinstance(item, (dict, list)):
            return '{}' if isinstance(item, dict) else '[]'
        return json.dumps('' if item is None else str(item), ensure_ascii=False)

    lines = []
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, (dict, list)) and item:
                lines += [f'{pad}{key}:', yaml_text(item, indent + 1)]
            else:
                lines.append(f'{pad}{key}: {scalar(item)}')
    else:
        for item in value:
            if isinstance(item, dict) and item:
                inner = yaml_text(item, indent + 1).split('\n')
                lines += [pad + '- ' + inner[0][len(pad) + 2:], *inner[1:]]
            else:
                lines.append(f'{pad}- {scalar(item)}')
    return '\n'.join(lines)


def source_entry(bibliography, key, relationship, note):
    """One source of `formalization.yaml`, from its entry in the bibliography.

    `id` is the most stable identifier the entry carries: its DOI, else its arXiv number, else its
    URL. An entry that carries none is identified by its key in `records/bibliography.bib`."""
    entry = {'title': bibliography_field(bibliography, key, 'title') or key}
    authors = bibliography_field(bibliography, key, 'author')
    if authors:
        entry['authors'] = [name.strip() for name in authors.split(' and ')]
    doi, eprint = (bibliography_field(bibliography, key, field) for field in ('doi', 'eprint'))
    entry['id'] = ('doi:' + doi if doi else 'arXiv:' + eprint if eprint
                   else bibliography_field(bibliography, key, 'url') or key)
    entry['relationship'] = relationship
    if note:
        entry['note'] = note
    return entry


def formalization(title, decision, bibliography, config, licence, models, library, compared, root_record, modules,
                  toolchain, stated=None, axioms=()):
    """`formalization.yaml` in the mathlib-initiative format v0.4, as far as the run can fill it.

    `axioms` are the axioms that Lean reports for the compared theorems. The format lists under
    `status.axioms` every axiom used, the standard ones among them.

    The classification, the description, the sources with their notes, the earlier formalisations and
    the account of fidelity (where the Lean statement departs from the proposition in words) are the
    selection's; the account of the compared theorem is the statement of the root's record, verbatim;
    authors and responsible maintainers are the configuration's and stay empty when it names none.
    An author for whom the configuration gives a GitHub login or an ORCID iD is entered as a mapping
    with the name and what is given of the two, the form in which the registry reads them; every other
    author, and every responsible maintainer, is entered by name.
    The entry that records a result as original carries the selection's grounds for that as its note.

    One source can come from the library stage instead of the selection: when the result is recorded as
    known and the root's record names a source, which the sources session entered after it had found a
    work that states the root, that work is listed with the relationship `independently-proves`, the
    registry's word for a new proof of a known published result.

    `stated` gives, for a compared theorem, its statement in words from its record; the alignment of that
    theorem carries it, and the selection's sentence where a record has none."""
    registry = decision['registry']
    names = [author['name'] for author in config['authors']]
    authors = [{'name': author['name'], **{key: author[key] for key in ('github', 'orcid') if author.get(key)}}
               if author.get('github') or author.get('orcid') else author['name'] for author in config['authors']]
    sources = []
    if registry.get('origin') == 'original':
        sources.append({'title': decision['sentence'], 'type': 'original-proof', 'relationship': 'other',
                        **({'note': registry['novelty']} if registry.get('novelty') else {})})
    sources += [source_entry(bibliography, source['key'], source['relationship'], source.get('note', ''))
                for source in registry.get('sources', [])]
    key = ((root_record or {}).get('meta') or {}).get('source')
    if registry.get('origin') != 'original' and key and key not in [s['key'] for s in registry.get('sources', [])]:
        sources.append(source_entry(bibliography, key, 'independently-proves',
                                    'The record of ' + (f'`{compared[0]}`, `records/{name_path(compared[0])}.md`,'
                                                        if compared else 'the proposition')
                                    + ' names this work as the place where that statement is found in '
                                    'the literature. The relationship says that the library proves the statement by a '
                                    'proof of its own, which does not come from this work. It does not say that this '
                                    'work proves it.'))
    review = config['human_review']
    if review['status'] == 'none':
        status = {'status': 'agent-reviewed', 'reviewers': [],
                  'notes': 'The review sessions of do-math judged every proof that the research published. AI sessions '
                           'then made the library of this package from the library of the research: they removed what '
                           'the presented proof does not use, and they may have simplified proofs, derived the '
                           'proposition from the main theorem, or added declarations that the paper states. Lean '
                           'compiled every such change, and the review sessions of the research did not judge them. No '
                           'person reviewed the proof or read the Lean statement against the proposition.'}
    else:
        status = {'status': review['status'], 'reviewers': list(review['reviewers']), 'notes': review['notes']}
    sections = (root_record or {}).get('sections', {})
    return {
        'version': 'v0.4',
        'project': {'name': title, 'description': decision['sentence'], 'authors': authors, 'license': licence,
                    'responsible_maintainers': names},
        'classification': {'arxiv': list(registry['arxiv']), 'msc2020': list(registry['msc2020'])},
        'sources': sources,
        'related_formalizations': [dict(item) for item in registry.get('related_formalizations', [])],
        'status': {'scope': sections.get('Statement', ''), 'sorry_count': 0, 'sorry_in_definitions': 0,
                   'axioms': list(axioms)},
        'automation': {'methods': [{'method': 'autonomous', 'models': list(models), 'framework': 'do-math',
                                    'tool_setup': release_of(toolchain)}]},
        'fidelity': {'divergences': registry.get('divergences', '')},
        'review': status,
        'alignment': {'namespace': library,
                      'statements': [{'source': (stated or {}).get(name) or decision['sentence'], 'lean': name,
                                      'module': modules[name],
                                      'status': 'proved'} for name in compared]}}


def registry_problems(lean_folder, licence):
    """The registry's rules that the pipeline controls, checked on the frozen `lean/` folder."""
    import yaml
    lean_folder = Path(lean_folder)
    problems = []
    for name in ('lean-toolchain', 'lakefile.toml', 'lake-manifest.json', 'Challenge.lean', 'Solution.lean',
                 'Check.lean', 'comparator.json', 'formalization.yaml'):
        if not (lean_folder / name).is_file():
            problems.append(f'lean/{name} is missing')
    if (lean_folder / 'lakefile.lean').exists():
        problems.append('lean/ holds lakefile.lean beside lakefile.toml; the registry wants exactly one')
    problems += lean_form_problems(lean_folder, lean_only=False)
    if (lean_folder / 'comparator.json').is_file():
        data = read_json(lean_folder / 'comparator.json')
        unknown = sorted(set(data) - set(COMPARATOR_REQUIRED) - set(COMPARATOR_OPTIONAL))
        lacking = [key for key in COMPARATOR_REQUIRED if key not in data]
        if unknown:
            problems.append('comparator.json has keys the registry does not accept: ' + ', '.join(unknown))
        if lacking:
            problems.append('comparator.json lacks ' + ', '.join(lacking))
        if not data.get('theorem_names'):
            problems.append('comparator.json names no theorem')
        if sorted(data.get('permitted_axioms', [])) != sorted(PERMITTED_AXIOMS):
            problems.append('comparator.json permits other axioms than the three')
    if (lean_folder / 'formalization.yaml').is_file():
        try:
            data = yaml.safe_load(read_text(lean_folder / 'formalization.yaml'))
        except yaml.YAMLError as error:
            return problems + [f'formalization.yaml is not YAML: {error}']
        project = data.get('project', {})
        text = lambda value: isinstance(value, str) and bool(value.strip())
        if not text(project.get('name')) or len(project['name']) > 300:
            problems.append('formalization.yaml: project.name is a nonempty text of at most 300 characters')
        if not text(project.get('description')) or len(project['description']) > 10_000:
            problems.append('formalization.yaml: project.description is a nonempty text of at most 10,000 characters')
        if project.get('license') != licence:
            problems.append(f'formalization.yaml: project.license is not {licence}, the licence of the package')
        arxiv = data.get('classification', {}).get('arxiv', [])
        msc = data.get('classification', {}).get('msc2020', [])
        if not 1 <= len(arxiv) <= 8 or not all(text(code) and ARXIV.fullmatch(code) for code in arxiv):
            problems.append('formalization.yaml: classification.arxiv holds one to eight arXiv categories')
        if not 1 <= len(msc) <= 8 or not all(text(code) and MSC.fullmatch(code) for code in msc):
            problems.append('formalization.yaml: classification.msc2020 holds one to eight MSC2020 codes')
        # The list may be empty: for a result that is recorded as known and whose research names no source, the
        # run cannot name one, and the report lists the field among what the user fills in.
        sources = data.get('sources') or []
        if not all(isinstance(s, dict) and text(s.get('title')) and s.get('relationship') in RELATIONSHIPS
                   for s in sources):
            problems.append('formalization.yaml: each entry of sources has a title and a relationship of '
                            + ', '.join(RELATIONSHIPS))
        if not all(isinstance(r, dict) and text(r.get('id')) for r in data.get('related_formalizations') or []):
            problems.append('formalization.yaml: each entry of related_formalizations has an id')
        methods = data.get('automation', {}).get('methods') or []
        if not methods or not all(isinstance(m, dict) and text(m.get('method')) for m in methods):
            problems.append('formalization.yaml: automation.methods is a nonempty list, each with a method')
        if not text(data.get('review', {}).get('status')):
            problems.append('formalization.yaml: review.status is a nonempty text')
    return problems


def freeze_hashes(package):
    """The SHA-256 of every file of `lean/` and `records/` of a package, and of the two folders."""
    package = Path(package)
    return {'folders': {name: tree_hash(package / name) for name in ('lean', 'records')},
            'files': {name + '/' + relative: sha256_file(path) for name in ('lean', 'records')
                      for relative, path in files_under(package / name).items()}}


# ----------------------------------------------------------------------------- stage 3: archive and ledger

def account_name():
    """The account name of the machine's user, which no file of a package may hold."""
    import getpass
    return getpass.getuser()


def account_pattern(account):
    """Where a text holds the account name: the name with no letter and no digit beside it.

    A short account name is a part of ordinary words, as `sam` is of "same" and `pat` of "path", and such a
    word is not the name. In a path or a sentence the name has a separator, a space or the end beside it."""
    return re.compile(rb'(?<![A-Za-z0-9])' + re.escape(account.encode('utf-8')) + rb'(?![A-Za-z0-9])')


def knowledge_archive(repository, commit, folder, name, account):
    """`<name>-knowledge.tar.xz` and `MANIFEST.md`: `canon/` and `knowledge/` of a commit, as Git stores them.

    One change is made to the members: the account name is replaced by `<account>` wherever it
    stands by itself (account_pattern), in a member's bytes and in its path, which also covers the home
    folder's path. The archive is the same for the same commit: members in Git's order, the commit's time
    on each, no owner."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    archive = folder / f'{name}-knowledge.tar.xz'
    stamp = commit_time(repository, commit)
    named = account_pattern(account) if account else None
    count = size = touched = 0
    with lzma.open(archive, 'wb', preset=6) as packed, tarfile.open(fileobj=packed, mode='w|', format=tarfile.PAX_FORMAT) as out:
        for path, data in git_members(repository, commit, ['canon', 'knowledge']):
            changed = named.sub(ACCOUNT.encode(), data) if named else data
            renamed = named.sub(ACCOUNT.encode(), path.encode('utf-8')).decode('utf-8') if named else path
            touched += changed != data or renamed != path
            info = tarfile.TarInfo(renamed)
            info.size, info.mtime, info.mode = len(changed), stamp, 0o644
            out.addfile(info, io.BytesIO(changed))
            count += 1
            size += len(changed)
    digest = sha256_file(archive)
    date = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(stamp))
    write_text(folder / 'MANIFEST.md', '\n'.join([
        '# The knowledge archive', '',
        f'`{archive.name}` holds the folders `canon/` and `knowledge/` of the research as its Git repository had them '
        'at one commit: the library with its records, the approaches tried, the understanding reached on each question, '
        'the evidence, and every published change with its review. Session transcripts were not in the repository and '
        'are not in the archive.', '',
        f'- Commit: `{commit}`', f'- Date of the commit: {date}', f'- Files: {count}',
        f'- Size unpacked: {size} bytes', f'- Size of the archive: {archive.stat().st_size} bytes',
        f'- SHA-256 of the archive: `{digest}`', '',
        (f'One change was made to the files. The account name of the machine on which the research ran is replaced by '
         f'`{ACCOUNT}` wherever it stood, which also covers the path of the home folder. {touched} files were touched '
         'by this. Other paths of that machine in the research\'s own records stand as they were written.' if touched
         else 'No file of the archive holds the account name of the machine on which the research ran, so the files are '
              'in the archive as the commit has them. Where a record in the archive mentions a file path of that '
              'machine, the path is kept as it was written; it is not a path of this package.'), '',
        '## Verifying and unpacking', '',
        '```text', f'sha256sum {archive.name}', f'tar -xJf {archive.name}', '```', '',
        'The first command prints the SHA-256 above. The second writes `canon/` and `knowledge/` into the current folder.',
        '']))
    return {'archive': archive.name, 'commit': commit, 'date': date, 'files': count, 'bytes': size,
            'archive_bytes': archive.stat().st_size, 'sha256': digest, 'touched': touched}


def archive_members(archive, wanted=lambda name: True):
    """The members of a knowledge archive that `wanted` accepts, as bytes by path."""
    found = {}
    with lzma.open(archive, 'rb') as packed, tarfile.open(fileobj=packed, mode='r|') as stream:
        for member in stream:
            if member.isreg() and wanted(member.name):
                found[member.name] = stream.extractfile(member).read()
    return found


def archive_names(archive):
    with lzma.open(archive, 'rb') as packed, tarfile.open(fileobj=packed, mode='r|') as stream:
        return [member.name for member in stream if member.isreg()]


def manifest_sha(manifest):
    """The SHA-256 that a knowledge archive's MANIFEST.md states."""
    found = re.search(r'SHA-256 of the archive: `([0-9a-f]{64})`', read_text(manifest))
    return found[1] if found else None


def ledger(members):
    """`ledger.json`: the research's reviewed record in time order, each line with the member it comes from.

    `members` are the archive's files under `knowledge/`, `canon/approaches/`, `canon/questions/` and
    `canon/history/`. Of the last, the lines are the approaches of statements whose proof was accepted
    later: the research moves those to `canon/history/<statement>/<number>-approaches/`.
    First the published events by their sequence numbers, each with the change's own title and
    description, the elements it added or replaced, review's reason and its judgment of what the
    change contributed, the questions it opened or resolved, and under `by` the kind of session whose
    work it carries. Then what was tried on each statement
    and what was understood of each question, numbered after the events."""
    load = lambda name: json.loads(members[name].decode('utf-8-sig')) if name in members else {}
    events = sorted((json.loads(data.decode('utf-8-sig')) for name, data in members.items()
                     if re.fullmatch(r'knowledge/events/[^/]+\.json', name)), key=lambda event: event['sequence'])
    rows = []
    for event in events:
        folder = 'knowledge/' + event['folder']
        row = {'event': event['sequence'],
               'date': time.strftime('%Y-%m-%d', time.gmtime(event['at'])) if event.get('at') else '',
               'kind': event['kind'], 'by': event.get('producer_role') or SESSION_OF.get(event['kind'], ''),
               'title': '', 'description': '', 'elements': [], 'review': '', 'contribution': '',
               'questions': [], 'record': folder}
        if event['kind'] == 'change':
            change, applied, assessment = (load(f'{folder}/{name}.json') for name in ('change', 'applied', 'assessment'))
            row.update(title=change.get('title', ''), description=change.get('description', ''),
                       elements=applied.get('added', []) + applied.get('replaced', []),
                       review=assessment.get('reason', ''), contribution=assessment.get('contribution', ''),
                       questions=[f"proposed {q['id']}: {q.get('statement', '')}" for q in change.get('questions', [])]
                       + [f"resolves {r.get('question', '')}" for r in change.get('resolutions', [])],
                       record=folder + '/change.json')
        elif event['kind'] == 'review':
            assessment = load(folder + '/assessment.json')
            findings = assessment.get('findings', [])
            row.update(title='A comprehensive review', review=' '.join(f.get('reason', '') for f in findings),
                       elements=sorted({name for f in findings for name in f.get('invalidates', []) + f.get('validates', [])}),
                       questions=[f'reopens {q}' for f in findings for q in f.get('reopens', [])],
                       record=folder + '/assessment.json')
        elif event['kind'] == 'organization':
            data, applied = load(folder + '/organization.json'), load(folder + '/applied.json')
            row.update(title='An organization of the canon', elements=applied.get('added', []),
                       questions=[f"merges {m['from']} into {m['into']}" for m in data.get('merge_questions', [])],
                       record=folder + '/organization.json')
        elif event['kind'] == 'questions':
            data = load(folder + '/questions.json')
            row.update(title='Questions placed by the operator', description=data.get('reason', ''),
                       questions=[f"{q['id']}: {q.get('statement', '')}" for q in data.get('questions', [])],
                       record=folder + '/questions.json')
        rows.append(row)
    number = max((row['event'] for row in rows), default=0)
    for prefix, kind in (('canon/approaches/', 'approach'), ('canon/questions/', 'question')):
        for name in sorted(members):
            if not name.startswith(prefix) or not name.endswith('.md'):
                continue
            number += 1
            text = members[name].decode('utf-8-sig').replace('\r\n', '\n')
            inner = PurePosixPath(name[len(prefix):])
            title = re.search(r'^title:\s*(.*)$', text, re.M)
            rows.append({'event': number, 'date': '', 'kind': kind, 'by': '',
                         'title': title[1].strip() if kind == 'approach' and title else inner.stem,
                         'description': text, 'elements': [path_name(inner.parent)] if kind == 'approach' else [],
                         'review': '', 'contribution': '', 'questions': [inner.stem] if kind == 'question' else [],
                         'record': name})
    retired = re.compile(r'canon/history/(.+)/\d+-approaches/[^/]+\.md')
    for name in sorted(members):
        found = retired.fullmatch(name)
        if not found:
            continue
        number += 1
        text = members[name].decode('utf-8-sig').replace('\r\n', '\n')
        title = re.search(r'^title:\s*(.*)$', text, re.M)
        rows.append({'event': number, 'date': '', 'kind': 'approach', 'by': '',
                     'title': title[1].strip() if title else PurePosixPath(name).stem, 'description': text,
                     'elements': [path_name(PurePosixPath(found[1]))], 'review': '', 'contribution': '',
                     'questions': [], 'record': name})
    return rows


def event_members(row, names):
    """The members of the archive that a ledger line points to: its record and the files beside it."""
    if row['kind'] in ('approach', 'question'):
        return [row['record']]
    folder = row['record'].rsplit('/', 1)[0] + '/'
    return [name for name in names if name.startswith(folder)]


# What the research's own words for a publication's source are, where the event does not carry one.
SESSION_OF = {'organization': 'organizer', 'questions': 'operator', 'review': 'review'}
# An entry of the history is two to four sentences, and an item of its list one clause. A longer entry retells
# the mathematics of its elements and is harder to read than the records it condenses, so the program refuses
# an entry beyond these bounds.
HISTORY_TEXT_WORDS, HISTORY_ITEM_WORDS = 120, 30
PUBLICATION = {'change': 'change', 'review': 'review of published proofs', 'organization': 'organization of the library',
               'questions': 'questions placed by the operator'}


def entry_problems(event, text, groups):
    """Where an entry of the history has not the form the timeline carries: its length and the shape of its list."""
    problems = []
    if len(text.split()) > HISTORY_TEXT_WORDS:
        problems.append(f'the entry of the event {event} has {len(text.split())} words; an entry is two to four '
                        f'sentences, at most {HISTORY_TEXT_WORDS} words, and names many elements in its list')
    if not isinstance(groups, list) or not all(
            isinstance(group, dict) and isinstance(group.get('group', ''), str) and isinstance(group.get('items'), list)
            and group['items'] and all(isinstance(item, str) and item.strip() for item in group['items'])
            for group in groups):
        return problems + [f'the list of the event {event} is an array of groups, each with "group" (a text, empty for '
                           'a list that is not divided) and "items" (a nonempty array of texts)']
    long = [item for group in groups for item in group['items'] if len(item.split()) > HISTORY_ITEM_WORDS]
    if long:
        problems.append(f'the list of the event {event} has {len(long)} items of more than {HISTORY_ITEM_WORDS} words; '
                        'an item is the name of an element, a colon and one clause')
    return problems


def timeline(entries, title):
    """`timeline.md` from the entries: one heading for each, so that a date or a publication is found at a glance.

    A publication's heading carries its number in the order of the research, its date and its kind. Under
    the heading stand the entry, the list of its elements where it has one, and the record it condenses."""
    lines = [f'# The history of the research on `{title}`', '',
             'Each entry says what happened at one point of the research and ends with the record it condenses. The '
             'path given for a record is its path inside the knowledge archive, the `.tar.xz` file in the folder '
             '`knowledge/` of this package. The archive unpacks into two folders, `canon/` and `knowledge/`, and every '
             'such path begins with one of them; none is a path of this package. The research proved more than the '
             'library of this package keeps: `lean/` holds the proof that the package presents, and a declaration '
             'that is named here and that `lean/` does not have is in the archive. A publication carries its number '
             'in the order of the research and its date. The entries make no claim of their own and give no proofs; '
             'the records do.', '']
    parts = ((tuple(PUBLICATION), 'Publications'), (('approach',), 'What was tried on each statement'),
             (('question',), 'What was understood of each question'))
    for kinds, heading in parts:
        chosen = [entry for entry in sorted(entries, key=lambda entry: entry['event']) if entry['kind'] in kinds]
        if not chosen:
            continue
        lines += ['## ' + heading, '']
        for entry in chosen:
            if entry['kind'] in PUBLICATION:
                head = ' \u00b7 '.join(part for part in (str(entry['event']), entry['date'], PUBLICATION[entry['kind']])
                                      if part)
            elif entry['kind'] == 'approach':
                head = '`' + (entry.get('elements') or [''])[0] + '`: ' + ' '.join(entry.get('title', '').split())
            else:
                head = 'Question `' + PurePosixPath(entry['record']).stem + '`'
            lines += ['### ' + head, '', ' '.join(entry['text'].split()), '']
            for group in entry.get('list') or []:
                items = ['- ' + ' '.join(item.split()) for item in group['items']]
                named = ' '.join(group.get('group', '').split())
                lines += (['- **' + named + '**'] + ['  ' + item for item in items]) if named else items
            if entry.get('list'):
                lines.append('')
            lines += [f"Record: `{entry['record']}`", '']
    return '\n'.join(lines)


# ----------------------------------------------------------------------------- stage 5: the documents

def fill(text, facts):
    """A text with every `{{facts.<key>}}` replaced; returns (text, the keys that `facts` does not have)."""
    missing = []

    def value(match):
        if match[1] not in facts:
            missing.append(match[1])
            return match[0]
        return str(facts[match[1]])

    return re.sub(r'\{\{facts\.([A-Za-z0-9_]+)\}\}', value, text), sorted(set(missing))


def registry_sources(path):
    """How many sources `formalization.yaml` names; the registry asks for one at the least."""
    import yaml
    path = Path(path)
    return len((yaml.safe_load(read_text(path)) or {}).get('sources') or []) if path.is_file() else 0


def package_facts(package, name, library, root, main, index, freeze, archive, timeline_entries, correspondence, cited,
                  title, toolchain, requires, models, sessions, commit):
    """`facts.json`: every figure of the documents, read from the finished products."""
    package = Path(package)
    modules = [path for relative, path in files_under(package / 'lean' / library).items() if relative.endswith('.lean')]
    top = package / 'lean' / (library + '.lean')
    modules += [top] if top.is_file() else []
    entries = index['entries']
    statements = correspondence.get('statements', [])
    return {'name': name, 'title': title, 'library': library, 'root': root, 'main': main,
            'toolchain': toolchain, 'requires': requires, 'pinned_commit': commit,
            'modules': len(modules), 'lines': sum(read_text(path).count('\n') for path in modules),
            'declarations': len(entries), 'theorems': sum(e['kind'] == 'theorem' for e in entries.values()),
            'definitions': sum(e['kind'] != 'theorem' for e in entries.values()),
            'records': sum(relative.endswith('.md') for relative in files_under(package / 'records')),
            'sources': len(bibliography_keys(read_text(package / 'records' / 'bibliography.bib')))
            if (package / 'records' / 'bibliography.bib').is_file() else 0,
            'registry_sources': registry_sources(package / 'lean' / 'formalization.yaml'),
            'compared': ', '.join(freeze['compared']),
            'axioms_root': ', '.join(freeze['axioms'].get(root, [])) or 'none',
            'axioms_main': ', '.join(freeze['axioms'].get(main, [])) or 'none',
            'timeline_entries': len(timeline_entries),
            'publications': sum(entry['kind'] in ('change', 'review', 'organization', 'questions')
                                for entry in timeline_entries),
            'archive': archive['archive'], 'archive_files': archive['files'], 'archive_bytes': archive['archive_bytes'],
            'archive_sha256': archive['sha256'],
            'statements': len(statements), 'cited_proved': len(cited),
            'statements_differing': sum((row.get('comparison') or {}).get('verdict') == 'differs' for row in statements),
            'models': ', '.join(models), 'sessions': sessions}


def provenance(registry, path):
    """What the README says of where the result comes from.

    The two texts are the selection's; the sources and the earlier formalisations are read from the
    frozen `formalization.yaml`, so the README lists them as the registry's file does."""
    import yaml
    data = yaml.safe_load(read_text(path)) or {}
    return {'settles': registry['settles'], 'novelty': registry['novelty'], 'origin': registry['origin'],
            'sources': data.get('sources') or [], 'related': data.get('related_formalizations') or []}


def provenance_lines(given):
    """The part of the README that says whose question the result settles, what was known, and from which works."""
    recorded = {'original': 'original, which there means a result that the formalisation presents first',
                'source-based': 'source-based, which there means a result that was presented elsewhere before'}
    relation = {'formalizes': 'The library formalises the result of this work.',
                'adapts': 'The library changes or extends the result of this work.',
                'independently-proves': 'This work has the result, and the proof in the library does not come from it.',
                'background': 'This work gives context and not the result.'}
    lines = ['### Where the result comes from', '', given['settles'].strip(), '',
             'In `lean/formalization.yaml`, the file that describes the package for a formal-proof registry, the '
             f"result is recorded as {recorded[given['origin']]}. " + given['novelty'].strip(), '']
    works = [source for source in given['sources'] if source.get('type') != 'original-proof']
    if works:
        lines += ['The works that `lean/formalization.yaml` lists as sources:', '']
        for source in works:
            head = source['title'] + (', ' + ', '.join(source['authors']) if source.get('authors') else '')
            parts = [head + (f" ({source['id']})" if source.get('id') else '') + '.',
                     relation.get(source.get('relationship'), ''), (source.get('note') or '').strip()]
            lines.append('- ' + ' '.join(part for part in parts if part))
        lines.append('')
    else:
        lines += ['`lean/formalization.yaml` lists no work as a source of the result.', '']
    if given['related']:
        lines += ['Earlier formal proofs that the records of the research name:', '']
        lines += ['- ' + ' '.join(part for part in (item['id'] + '.', (item.get('note') or '').strip()) if part)
                  for item in given['related']]
        lines.append('')
    else:
        lines += ['The records of the research name no earlier formal proof of this result.', '']
    return lines


def readme_text(facts, root_words, root_statement, main_statement, outline, obtained, check_output, config, licence,
                fails, cited_rows, origin, instances=(), not_done=()):
    """`README.md` of a package. The two prose sections come from a session; every other sentence is written here.

    `origin` is what `provenance` returns; its texts are the selection's and stand under the result.
    `instances` are the statements that the paper proves from a cited general theorem, as the
    correspondence file lists them. `not_done` are the checks of the run that were not made, each
    in a sentence."""
    review = config['human_review']
    human = ('No person reviewed the proof, and no person read the Lean statement against the proposition in words.'
             if review['status'] == 'none' else
             f"Review by a person: {review['status']}"
             + (', by ' + ', '.join(review['reviewers']) if review['reviewers'] else '') + '.'
             + (' ' + review['notes'].strip() if review['notes'].strip() else ''))
    same = facts['main'] == facts['root']
    lines = [f"# {facts['title']}", '']
    if config['authors']:
        lines += [', '.join(author['name'] for author in config['authors']), '']
    lines += ['## The result', '', root_words.strip(), '',
              f"In Lean, the proposition is the theorem `{facts['root']}` of the library `{facts['library']}`:", '',
              '```lean', root_statement, '```', '']
    if not same:
        lines += [f"The library proves it from its main theorem, `{facts['main']}`:", '', '```lean', main_statement, '```', '']
    lines += provenance_lines(origin)
    lines += ['## Outline of the proof', '', outline.strip(), '',
              '## How the result was obtained', '', obtained.strip(), '',
              '## What was checked, and what was not', '',
              f"- Lean compiled the library with `lake build` on {release_of(facts['toolchain'])}"
              + (f" with {facts['requires']}" if facts['requires'] else '') + ': '
              f"{facts['modules']} modules, {facts['lines']} lines, {facts['declarations']} public declarations.",
              f"- Lean reports for `{facts['root']}` the axioms: {facts['axioms_root']}."
              + ('' if same else f" For `{facts['main']}`: {facts['axioms_main']}."),
              '- A script compared the definitions and the statement of the proposition with their first form, which '
              'was fixed before the research began: the definition files byte for byte, the statement by the term that '
              'Lean elaborates. They are the same.',
              f"- Every public declaration has a record under `records/` ({facts['records']} records). An AI session "
              'wrote each record from the Lean text, and an AI session that did not write it compared it with that text.',
              f"- The paper states {facts['statements']} numbered statements. An AI session compared each with the "
              'declaration it states, and `paper/correspondence.json` has its verdict for each.'
              + (f" {facts['statements_differing']} of them still differ from their declarations."
                 if facts.get('statements_differing') else ''),
              "- The library is not the library of the research as the research's own reviews judged it. AI sessions cut "
              'that library down to the proof presented here and, where it served the presentation, simplified proofs, '
              'derived the proposition from the main theorem, or added declarations that the paper states. Lean compiled '
              'the result. The reviews of the research did not judge these changes.',
              '- The research, the library, the records, the paper and this document were produced by AI sessions run '
              f"by do-math. The sessions that made this package from the research ran on {facts['models']}. do-math is "
              'a program that conducts mathematical research in Lean: its sessions state and prove in Lean, other '
              'sessions review each publication, and what the reviews accept becomes the library with its records. '
              f'{human}',
              '- Not checked: the files under `lean/` that are prepared for a formal-proof registry, which the last '
              "section of this document describes. That registry's verifier was not run on them, and the "
              'classification codes in `lean/formalization.yaml` were checked for their form and not against its '
              'lists.',
              *(['- Not made: some of the checks that the items above describe. A safeguard of the AI system stopped '
                 'the session that had the task, each time the session was started, so the check was recorded as not '
                 'done and the rest of the work went on. These checks were not made: '
                 + '; '.join(f'({number}) {what}' for number, what in enumerate(not_done, 1)) + '.']
                if not_done else []), '',
              '## Building', '',
              f"The library is built with {release_of(facts['toolchain'])}"
              + (f" and {facts['requires']}" if facts['requires'] else '') + '. Lean is installed through elan, its '
              "toolchain manager, as Lean's own installation instructions describe. elan reads "
              '`lean/lean-toolchain`, fetches that release and provides the command `lake`. In the folder `lean/`:', '',
              '```text', 'lake build', 'lake env lean Check.lean', '```', '',
              'The first command compiles the library, and with it `Challenge.lean` and `Solution.lean`. '
              '`Challenge.lean` states the compared theorems without their proofs, for the comparison that a '
              'formal-proof registry makes, so Lean warns there, once for each of them, that a declaration uses '
              '`sorry`. The warnings concern that one file; no declaration of the library uses `sorry`. The second '
              'command prints the statements '
              'and the axioms they depend on. For the files of this folder it prints:', '',
              '```text', check_output.strip(), '```', '',
              '## What is in this folder', '',
              f"- `lean/`: the library `{facts['library']}`, its build files, and the files a formal-proof registry "
              'compares (`Challenge.lean`, `Solution.lean`, `comparator.json`, `formalization.yaml`).',
              '- `records/`: one record for each public declaration, and `bibliography.bib`.',
              '- `dependency-map/`: [the map of what the proof rests on](dependency-map/dependency_map.html).',
              '- `paper/`: [the paper](paper/paper.pdf), its source, and `correspondence.json`, which names the '
              'declaration behind each numbered statement.',
              f"- `history/`: [the timeline of the research](history/timeline.md), {facts['timeline_entries']} entries.",
              f"- `knowledge/`: `{facts['archive']}`, the research's own record ({facts['archive_files']} files), with "
              '[its manifest](knowledge/MANIFEST.md).',
              '- `MANIFEST.sha256`: the SHA-256 of every other file of this folder.', '',
              '## The paper', '',
              'The paper proves the result for a mathematical reader and mentions no formal proof.'
              + (' It attributes these statements to the literature, each to the source that '
                 '`paper/correspondence.json` names for it, and the library proves each of them formally: '
                 + ', '.join(f'`{name}`' for name in cited_rows) + '.' if cited_rows else '')
              + (' These statements it proves from a general theorem of the literature, which it cites, by '
                 'specialising that theorem: ' + ', '.join(f"`{entry['element']}`" for entry in instances)
                 + '. `paper/correspondence.json` names the theorem for each. The library does not rest on the cited '
                   'theorems; it proves each of these statements by an argument of its own.' if instances else ''), '',
              '## The licence', '',
              f'Everything in this folder is under {licence}; the text is in [LICENSE](LICENSE).', '',
              '## The registry', '',
              f"The files under `lean/` are prepared for a formal-proof registry that runs Lean's comparator. It "
              f"compares: {facts['compared']}. A submission is this folder published as a repository of its own, with "
              '`lean` named as the project directory.']
    if not config['authors']:
        lines += ['`lean/formalization.yaml` names no author and no responsible maintainer; the registry requires both.']
    lines += [rule + '.' for rule in fails]
    return '\n'.join(lines) + '\n'


def said(text, length=700):
    """A text on one line, cut at a word where it is longer than `length`."""
    text = ' '.join(str(text).split())
    return text if len(text) <= length else text[:length].rsplit(' ', 1)[0] + ' ...'


def finding_lines(findings):
    """What the reader of the package found, one line for each: the file, the passage, and the problem."""
    return [f"- {finding['file']}" + (f", at \"{said(finding['quote'], 200)}\"" if finding['quote'].strip() else '')
            + f": {said(finding['problem'], 1200)}" for finding in findings]


def closed_lines(closed):
    """What the paper command closed without a person, one line for each, as `decisions.md` has it."""

    lines = []
    for entry in closed:
        if entry['kind'] == 'removed' and entry.get('source'):
            lines.append(f"- Removed from {entry.get('where') or 'the manuscript'}: \"{said(entry['quote'])}\" It said of "
                         f"the cited work `{entry['source']}` something that the words copied from that work do not "
                         f"show. {said(entry.get('difference', ''))}")
        elif entry['kind'] == 'removed':
            lines.append(f"- Removed from {entry.get('where') or 'the manuscript'}: \"{said(entry['quote'])}\" It asserted: "
                         f"{said(entry.get('asserts') or 'not said')} The declaration that came nearest is "
                         f"`{entry.get('nearest')}`. {said(entry.get('difference', ''))}")
        elif entry['kind'] == 'restated':
            after = 'found the two the same.' if entry['verdict'] == 'same' else \
                'still found a difference: ' + said(entry.get('difference_after', '')) if entry['verdict'] == 'differs' \
                else 'was not made.'
            lines.append(f"- {entry['number']} (`{entry['label']}`) was restated as its declaration `{entry['element']}` "
                         f"says it. Before: \"{said(entry['before'])}\" The comparison had found: "
                         f"{said(entry['difference'])} After: \"{said(entry['after'])}\" The comparison after the "
                         f'restatement {after}')
        elif entry['kind'] == 'differs':
            lines.append(f"- {entry['number']} (`{entry['label']}`) differs from its declaration `{entry['element']}` after "
                         f"a repair of the typesetting changed its text, and stays as it is: {said(entry['difference'])}")
        else:
            lines.append(f"- A line of the typeset paper is wider than the text block: {said(entry.get('problem', ''))}")
    return lines


def manifest_text(package):
    """`MANIFEST.sha256`: the SHA-256 and the path of every other file of a package."""
    return ''.join(f'{sha256_file(path)}  {relative}\n' for relative, path in files_under(package).items()
                   if relative != 'MANIFEST.sha256')


# ----------------------------------------------------------------------------- stage 6: the stand-alone check

WRITTEN = ('README.md', 'MANIFEST.sha256', 'knowledge/MANIFEST.md', 'history/timeline.md', 'lean/lean-toolchain',
           'lean/lakefile.toml', 'lean/lake-manifest.json', 'lean/Check.lean', 'lean/Challenge.lean',
           'lean/Solution.lean', 'lean/comparator.json', 'lean/formalization.yaml', 'paper/paper.tex',
           'paper/references.bib', 'paper/correspondence.json')


def standalone_problems(package, work, account, freeze):
    """The final check of a package, made once: it stands alone and is what the freeze hashed.

    Every relative link of its Markdown and HTML resolves inside it; no file and no member of the
    archive holds the account name; no document the pipeline wrote holds a drive path or the work
    folder's path; every text file ends its lines with LF; `lean/` and `records/` have the hashes of
    the freeze; every line of `MANIFEST.sha256` holds and every other file has a line.

    A text file is a file that is UTF-8 and holds no NUL byte. The archive and the typeset paper are
    not, so the members of the archive, which are the research's own bytes, are not read for this."""
    package = Path(package).resolve()
    files = files_under(package)
    problems = []
    for relative, path in files.items():
        if not relative.endswith(('.md', '.html', '.htm')):
            continue
        for found in LINK.findall(path.read_text(encoding='utf-8', errors='replace')):
            target = (found[0] or found[1]).split('#')[0].split('?')[0]
            if not target or re.match(r'[A-Za-z][A-Za-z0-9+.-]*:', target) or target.startswith('//'):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.is_relative_to(package) or not resolved.exists():
                problems.append(f'{relative}: the link {target} does not resolve inside the package')
    if account:
        named = account_pattern(account)
        for relative, path in files.items():
            # The archive is read by its members. In its packed bytes the name can stand only by chance.
            packed = relative.endswith('-knowledge.tar.xz')
            if (not packed and named.search(path.read_bytes())) or named.search(relative.encode('utf-8')):
                problems.append(f'{relative} holds the account name')
            if packed:
                held = [name for name, data in archive_members(path).items()
                        if named.search(data) or named.search(name.encode('utf-8'))]
                problems += [f'{relative}: the member {name} holds the account name' for name in held]
    for relative, path in files.items():
        data = path.read_bytes()
        if b'\r' in data and b'\0' not in data:
            try:
                data.decode('utf-8')
            except UnicodeDecodeError:
                continue
            problems.append(f'{relative} has line endings other than LF')
    places = [str(Path(work).resolve()), Path(work).resolve().as_posix()]
    for relative in WRITTEN:
        if relative not in files:
            continue
        text = files[relative].read_text(encoding='utf-8', errors='replace')
        found = (DRIVE_PATH_IN_MARKUP if relative.endswith(('.md', '.tex', '.bib')) else DRIVE_PATH).search(text)
        if found:
            problems.append(f'{relative} holds a drive path: {text[found.start():found.start() + 40]!r}')
        if any(place in text for place in places):
            problems.append(f"{relative} holds the work folder's path")
    now = freeze_hashes(package)
    for name in ('lean', 'records'):
        if now['folders'][name] != freeze['folders'][name]:
            changed = sorted(key for key in set(now['files']) | set(freeze['files']) if key.startswith(name + '/')
                             and now['files'].get(key) != freeze['files'].get(key))
            problems.append(f'{name}/ is not what the freeze hashed: ' + ', '.join(changed))
    listed = {}
    manifest = package / 'MANIFEST.sha256'
    for line in read_text(manifest).splitlines() if manifest.is_file() else []:
        digest, _, relative = line.partition('  ')
        listed[relative] = digest
    if not manifest.is_file():
        problems.append('MANIFEST.sha256 is missing')
    for relative, digest in listed.items():
        if relative not in files:
            problems.append(f'MANIFEST.sha256 lists {relative}, which the package does not have')
        elif sha256_file(files[relative]) != digest:
            problems.append(f'MANIFEST.sha256 does not hold for {relative}')
    problems += [f'MANIFEST.sha256 has no line for {relative}' for relative in files
                 if relative not in listed and relative != 'MANIFEST.sha256']
    return problems


def add_solved_entry(readme, name, entry):
    """Add one entry under "Solved problems" in the repository's README, creating the section when it is absent.

    The entry is one list item. An entry for the same package is not added twice."""
    readme = Path(readme)
    text = read_text(readme) if readme.is_file() else ''
    if f'(solved/{name}/README.md)' in text:
        return False
    lines = text.split('\n')
    heading = next((i for i, line in enumerate(lines) if re.fullmatch(r'#+\s*Solved problems\s*', line)), None)
    if heading is None:
        body = text.rstrip('\n')
        write_text(readme, (body + '\n\n' if body else '') + '## Solved problems\n\n' + entry + '\n')
        return True
    level = len(lines[heading]) - len(lines[heading].lstrip('#'))
    end = next((i for i in range(heading + 1, len(lines)) if re.match(r'#{1,' + str(level) + r'}\s', lines[i])), len(lines))
    while end > heading + 1 and not lines[end - 1].strip():
        end -= 1
    blank = [''] if end == heading + 1 else []
    lines[end:end] = blank + [entry] + ([''] if end < len(lines) and lines[end].strip() else [])
    write_text(readme, '\n'.join(lines))
    return True
