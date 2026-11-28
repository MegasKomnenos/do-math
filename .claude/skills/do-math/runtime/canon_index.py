"""The index of the canon: the tree in which the canon is filed, with a description at each level.

The canon is filed in folders, modules and elements. An element has its self-description in its record,
and this module holds what the two levels above it have: the line of a module and the description of a
folder. A folder is a directory under the library's module root that holds at least one module, at any
depth, and it is named like a Lean name: the directory `lean/Lib/A/B` is the folder `Lib.A.B`. The
library itself is the top of the index and is no folder. A module that lies directly under the library,
such as `Lib.Defs`, has no folder above it and stands at the top beside the folders.

Layout under <instance>/canon/:
    descriptions/modules/<Module path>.md   the line of module `Lib.A.B` is descriptions/modules/Lib/A/B.md
    descriptions/folders/<Folder path>.md   the description of folder `Lib.A` is descriptions/folders/Lib/A.md
    descriptions.json                       the summary, gathered by machine at each publication (gather)
    history/descriptions/modules|folders/<path>/   what a replacement or a removal left behind

No Lean file carries a description, so publishing one compiles nothing. The reading commands take the
texts from the summary and read no description file. See ../reference/canon.md for the commands.

This module imports `canon` and is imported by it only inside the functions that need it, as `canon`
imports the Lean broker.
"""
import difflib
import hashlib
import json
from pathlib import Path

from canon import Canon, CanonError
from runtime_support import read_json, replace_file, write_text

# The two kinds of description, each with the folder that holds its files and its key in the summary.
KINDS = {'module': 'modules', 'folder': 'folders'}
# A folder that does not follow a natural boundary says so in the last paragraph of its description, which
# begins with this label (parse_description, due_text).
BOUNDARY = 'Boundary:'
NO_DESCRIPTION = '(no description yet; open the folder to see what it holds)'
NO_LINE = '(no line yet)'
# The different purposes on which `prepare` asks a description that a change carries to have taken the blind
# descent test (canon_tool.description_errors).
TESTS_REQUIRED = {'module': 1, 'folder': 3}


# ----------------------------------------------------------------------------- the text of a description

def paragraphs(text):
    """The paragraphs of a text: its lines without the blanks around them, cut where a line is empty."""
    found, current = [], []
    for line in text.lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        line = line.strip()
        if line:
            current.append(line)
        elif current:
            found.append('\n'.join(current))
            current = []
    if current:
        found.append('\n'.join(current))
    return found


def normalise(text):
    """The one form in which a description is stored and compared: its paragraphs with one empty line
    between them, `\\n` line ends and one trailing newline."""
    return '\n\n'.join(paragraphs(text)) + '\n'


def text_sha(text):
    """The identity of a description's text, as the receipt of a blind descent test records it.

    It is taken of the normalised text, so the text as a session wrote it and the text as the canon
    stores it have the same identity."""
    return hashlib.sha256(normalise(text).encode('utf-8')).hexdigest()


def one_line(text):
    return ' '.join(text.split())


def parse_description(text, kind, what):
    """The normalised text of a module line (`kind` 'module') or a folder description ('folder').

    `what` names the file in the message of a refusal. The text is shown inside views that have headings
    of their own, so no line of it begins a heading or a code block. A module line is one paragraph. A
    folder description is one or more, and its last paragraph may begin with `Boundary:`."""
    parts = paragraphs(text)
    if not parts:
        raise CanonError(f'{what} is empty; a description says what lies beneath in plain sentences')
    if any(line.startswith(('#', '```')) for part in parts for line in part.split('\n')):
        raise CanonError(f'{what}: a line begins with "#" or with three backticks. The text is shown inside views '
                         'that have headings of their own, so write it as plain paragraphs and break the line '
                         'elsewhere')
    if kind == 'module' and len(parts) > 1:
        raise CanonError(f'{what}: a module line is one paragraph, a line or two; this text has an empty line '
                         'inside')
    if kind == 'folder':
        marked = [number for number, part in enumerate(parts) if part.startswith(BOUNDARY)]
        if marked and (marked != [len(parts) - 1] or len(parts) == 1 or not parts[-1][len(BOUNDARY):].strip()):
            raise CanonError(f'{what}: "{BOUNDARY}" begins the last paragraph of a folder description and no other. '
                             'The paragraphs before it say what the folder holds, and the text after the label '
                             'says in what the folder departs from a natural boundary')
    return '\n\n'.join(parts) + '\n'


def boundary_of(text):
    """The `Boundary:` paragraph of a folder description without its label, on one line; None when it has none."""
    parts = paragraphs(text)
    if len(parts) > 1 and parts[-1].startswith(BOUNDARY):
        return one_line(parts[-1][len(BOUNDARY):])
    return None


# ----------------------------------------------------------------------------- names and files

def description_file(root, kind, name):
    """The file of a description under a canon folder or a candidate folder; it follows the module's own path."""
    return Path(root) / 'descriptions' / KINDS[kind] / ('/'.join(name.split('.')) + '.md')


def described_files(root, kind):
    """Each description file of one kind under a canon folder or a candidate folder, as (name, path), by name.

    The name is read off the path, so a path component with a dot in it would give the name of another
    module or folder, and such a file is refused."""
    base = Path(root) / 'descriptions' / KINDS[kind]
    found = []
    for path in sorted(base.rglob('*.md')) if base.is_dir() else []:
        if not path.is_file():
            continue
        parts = path.relative_to(base).with_suffix('').parts
        if any('.' in part for part in parts):
            raise CanonError(f'descriptions/{KINDS[kind]}/{path.relative_to(base).as_posix()}: the path of a '
                             'description follows the name of its module or folder, one component for each '
                             'part of the name, as descriptions/modules/Lib/A/B.md does for the module Lib.A.B')
        found.append(('.'.join(parts), path))
    return sorted(found)


def candidate_descriptions(candidate):
    """The descriptions a candidate folder carries: {'modules': {name: text}, 'folders': {name: text}}.

    Each text is checked and normalised (parse_description). A folder without `descriptions/` gives two
    empty maps, which is how every candidate made before the index had descriptions looks. The folder of an
    operator's `describe` command has the same layout and is read with this as well."""
    found = {}
    for kind, key in KINDS.items():
        found[key] = {name: parse_description(path.read_text(encoding='utf-8-sig'), kind,
                                              f'descriptions/{key}/' + '/'.join(name.split('.')) + '.md')
                      for name, path in described_files(candidate, kind)}
    return found


def check_reports(values, where):
    """The form of a list of reports about the index; CanonError otherwise.

    An entry says that a session with the given purpose was not led by the named description to the named
    element. A peer writes its reports in the file descriptions/reports.json of its candidate
    (candidate_reports), and a review writes its own under `index_reports` in its assessment. `where` names
    the list in the message of a refusal. Whether the names exist is asked where the canon is at hand
    (canon_tool.description_errors, check.assessment_check)."""
    if not isinstance(values, list):
        raise CanonError(f'{where} is an array')
    for item in values:
        if (not isinstance(item, dict) or set(item) != {'description', 'element', 'purpose'}
                or not all(isinstance(value, str) and value.strip() for value in item.values())):
            raise CanonError(f'an entry of {where} has exactly "description", the name of a folder or module, '
                             '"element", the name of an element, and "purpose", each as nonempty text')
    return values


# The file of a candidate in which a peer reports that a description did not lead it to an element.
REPORTS = 'descriptions/reports.json'


def candidate_reports(candidate):
    """The reports about the index that a candidate carries in descriptions/reports.json; none without the file.

    The reports stand in a file of their own and in no key of change.json. The programs from before the
    index had descriptions refuse a change.json that has a key they do not know, and they read nothing
    under descriptions/, so a candidate with this file is one they still read. The file is a file of the
    candidate like every other: it belongs to the identity under which the candidate is prepared and
    frozen."""
    path = Path(candidate) / REPORTS
    if not path.is_file():
        return []
    try:
        values = read_json(path)
    except ValueError as exc:
        raise CanonError(f'{REPORTS} is not JSON ({exc})') from None
    return check_reports(values, REPORTS)


# The two ends of a frozen candidate at which nothing of it is published, as a kept report names them under
# `origin` (Runner.keep_reports), each with the words in which a listing says where the report came from.
KEPT = {'excluded': 'candidate that the review {review} excluded',
        'publication_failed': 'candidate that the review {review} accepted and whose publication failed'}


def kept_reports(instance):
    """The reports of the candidates that were not published, and of their reviews.

    A candidate that review excludes is not published, and neither is one that review accepted and that
    could not be published on the canon as it then was, whose work goes to a new peer. Their reports
    reach no published folder. The runner keeps them in <instance>/runner/index-reports.jsonl when it
    closes such a review (Runner.keep_reports), one line for each: `at`, `sequence` (the sequence of the
    latest publication at that time), `by` (`peer` or `review`), `review` (the session of the review),
    `origin` (a key of KEPT), `description`, `element` and `purpose`. A line without `origin` is one of an
    excluded candidate. A runner that ended between writing the lines and saving its state writes them
    once more, so the reports of one review that say the same are given once here. A line that cannot be
    read as its form, as one cut off when its process was ended, is left out. The file is read as bytes
    and each line is decoded by itself, so a line cut inside a character of several bytes, which is no
    UTF-8, is left out like any other cut line and does not make the file unreadable. An instance in
    which no such candidate carried a report has no such file.

    A runner that ended after it had kept the reports of a failed publication, and before it saved that
    the work goes to a new peer, left the publication in its state, and the next runner carries it on
    and can publish the candidate. Its reports are then those of a published change, and the lines kept
    of the failed publication say of the same reports what is no longer true. So a line whose origin is
    a failed publication is left out when a published change has the review of that line as its review
    session (published_reviews)."""
    path = Path(instance) / 'runner' / 'index-reports.jsonl'
    try:
        lines = path.read_bytes().splitlines()
    except OSError:
        return []
    found, seen, published = [], set(), None
    for line in lines:
        try:
            entry = json.loads(line.decode('utf-8'))
        except ValueError:
            continue
        if not isinstance(entry, dict):
            continue
        entry.setdefault('origin', 'excluded')
        if entry['origin'] not in KEPT or type(entry.get('sequence')) is not int or not all(
                isinstance(entry.get(key), str) for key in ('by', 'review', 'description', 'element', 'purpose')):
            continue
        if entry['origin'] == 'publication_failed':
            # Read only where such a line stands: one small file for each published change.
            published = published_reviews(instance) if published is None else published
            if entry['review'] in published:
                continue
        key = tuple(entry[key] for key in ('review', 'origin', 'by', 'description', 'element', 'purpose'))
        if key not in seen:
            seen.add(key)
            found.append(entry)
    return found


def published_reviews(instance):
    """The review sessions of the published changes: `review_session` in provenance.json of the folder of
    each (Runner.publish). A folder without that file, or with one that cannot be read, names none."""
    found = set()
    for path in (Path(instance) / 'knowledge' / 'changes').glob('*/provenance.json'):
        try:
            review = read_json(path).get('review_session')
        except (OSError, ValueError, AttributeError):
            continue
        if isinstance(review, str):
            found.add(review)
    return found


def open_reports(model, summary, kept=()):
    """The reports about the index that no description has answered yet, in the order of a listing:
    [{'from', 'description', 'element', 'purpose', 'needs', 'has'}].

    A report says that a description did not lead a session to an element. The reports of the published
    changes are in the model (knowledge.change_event), and `kept` are those of the candidates that were
    not published (kept_reports). A report is answered by the description it names once that description
    was written or confirmed against a canon that showed the report: the session that prepared it could
    read the report in `index --due`, and `prepare` named it (canon_tool.build_candidate). What says so is
    the `revision` of the description, the revision of the canon at that preparation, or the one the
    operator gave (apply_descriptions). The sequence of its publication does not say it: a description can
    be published after a report and have been written before the report existed.

    - A report of a published change, whose sequence is s, is answered by a description of revision s or
      later: the canon at revision s holds that change.
    - A report that the runner kept, at a time when the canon had revision q, is answered by a
      description of a revision later than q. One prepared at q may have been prepared before the report
      was kept, since keeping a report publishes nothing and leaves the revision as it is. Such a report
      can therefore stay listed after a publication whose session did read it, and it leaves with the
      next writing or confirmation at a later revision.

    `needs` is the revision from which a description answers the report, and `has` the revision of the
    description now, None where there is none yet. A name that is both a module and a folder has two
    descriptions, and the report stays until both answer it; `has` is then the earlier of the two. A
    report whose module or folder is no longer in the canon is not listed. `from` says where the report
    came from: the published change or the candidate, the revision of the canon then, and whether the
    peer or the review made it."""
    existing = {'modules': set(model['modules']), 'folders': set(folders_of(model['modules']))}
    sources = ([(f"published change {report['change']}", report['sequence'], report) for report in model['index_reports']]
               + [(KEPT[report['origin']].format(review=report['review']), report['sequence'] + 1, report)
                  for report in kept])
    found = []
    for source, needs, report in sources:
        name = report['description']
        described = [summary[key].get(name) for key in KINDS.values() if name in existing[key]]
        if described and not all(entry and entry['revision'] >= needs for entry in described):
            found.append({'from': f"{source} · revision {report['sequence']} · from the {report['by']}",
                          'description': name, 'element': report['element'], 'purpose': report['purpose'],
                          'needs': needs,
                          'has': min(entry['revision'] for entry in described) if all(described) else None})
    return found


def read_receipt(candidate):
    """`descriptions/tests.json` of a candidate as an object; an empty one without the file or where it is no object."""
    path = Path(candidate) / 'descriptions' / 'tests.json'
    try:
        data = read_json(path) if path.is_file() else {}
    except ValueError:
        data = {}
    return data if isinstance(data, dict) else {}


def test_results(candidate):
    """The results of the blind descent test in a candidate's `descriptions/tests.json`; none without the file.

    The file is written by the `descent-test` command. A file that cannot be read as its form counts as
    no receipt. A publication reads the results with this, to say whether a description was tested.
    Whether the file is the receipt of a test that ran is asked by `prepare` (taken_results)."""
    results = read_receipt(candidate).get('results')
    return [item for item in results if isinstance(item, dict)] if isinstance(results, list) else []


def taken_results(candidate, instance, session):
    """The results of a candidate's receipt when a blind descent test of this session produced them: (results, refusal).

    The command `descent-test` does its work in a folder under <instance>/runner/search/ and writes the
    receipt from that folder's result, with the name of the folder under `work` (search.descent_test_command).
    `prepare` counts the receipt only when that folder is there, its request names this session as the
    caller, and its result holds the very results of the receipt. A file that was written or changed by
    hand names no such folder or holds other results, and what it says was not found by a reader.

    Without the file there are no results and no refusal: `prepare` then asks each description for its
    test. Otherwise `refusal` says in a sentence why the file does not count, and the results are empty."""
    if not (Path(candidate) / 'descriptions' / 'tests.json').is_file():
        return [], None
    data = read_receipt(candidate)
    results, work = data.get('results'), data.get('work')
    home = Path(instance) / 'runner' / 'search'
    why = None
    if not isinstance(results, list) or not isinstance(work, str) or not work or Path(work).name != work:
        why = 'it names no test that was taken'
    else:
        try:
            request, result = read_json(home / work / 'request.json'), read_json(home / work / 'result.json')
        except (OSError, ValueError):
            request = result = None
        tests = result.get('tests') if isinstance(result, dict) else None
        if not isinstance(request, dict) or not isinstance(tests, dict):
            why = f'the test it names, {work}, has no result in this instance'
        elif request.get('kind') != 'descent-test' or request.get('caller') != session:
            why = f'the test it names, {work}, was not taken for this session'
        elif tests.get('results') != results:
            why = f'its results are not those of the test it names, {work}'
    if why:
        return [], ('descriptions/tests.json is not the receipt of a blind descent test of this session: ' + why
                    + '. The canon command descent-test takes the test and writes the file; run it, and then '
                    'prepare again')
    return [item for item in results if isinstance(item, dict)], None


def results_for(results, kind, name, text):
    """The results that were taken on this description with the text it has now."""
    sha = text_sha(text)
    return [item for item in results
            if item.get('target') == name and item.get('kind') == kind and item.get('text_sha') == sha]


# ----------------------------------------------------------------------------- the tree

def modules_of(model):
    """Every module of the structural index with its elements: {module name: [element names in name order]}.

    A module that declares no element, such as one that holds private helpers only, is a module of the
    canon all the same and has an empty list."""
    found = {module: [] for module in model['modules']}
    for name, element in model['elements'].items():
        found.setdefault(element['module'], []).append(name)
    return {module: sorted(found[module]) for module in sorted(found)}


def folders_of(names):
    """The folders of the canon, read off the names of its modules: every directory above a module, below the library."""
    found = set()
    for name in names:
        parts = name.split('.')
        for length in range(2, len(parts)):
            found.add('.'.join(parts[:length]))
    return sorted(found)


def parent(name, library):
    """The folder that holds a folder or a module, or the name of the library for one that stands at the top."""
    return '.'.join(name.split('.')[:-1]) or library


def children(names, library, parent_name):
    """What lies directly inside a folder, or directly under the library when `parent_name` is the library:
    (folders, modules), each in name order. `names` are the names of the modules of the canon."""
    names = list(names)
    return (sorted(folder for folder in folders_of(names) if parent(folder, library) == parent_name),
            sorted(module for module in names if parent(module, library) == parent_name))


def counts(modules):
    """For every folder, the number of modules and of elements beneath it at any depth: {folder: (modules, elements)}."""
    found = {}
    for module, elements in modules.items():
        parts = module.split('.')
        for length in range(2, len(parts)):
            entry = found.setdefault('.'.join(parts[:length]), [0, 0])
            entry[0] += 1
            entry[1] += len(elements)
    return {folder: tuple(entry) for folder, entry in found.items()}


def level_items(names, library, summary, parent_name, overlay=None):
    """The items of one level with their descriptions, as a blind reader is given them: [{'name', 'kind', 'text'}].

    The level is what lies directly inside `parent_name`. `names` are the module names to count as present,
    so a caller adds the modules a candidate brings. `overlay` holds the texts of a candidate in the form of
    candidate_descriptions, and they are laid over those of the summary. `text` is None for an item that
    has no description. Folders come first, then modules, each in name order."""
    overlay = overlay or {'modules': {}, 'folders': {}}
    inside, direct = children(names, library, parent_name)
    items = []
    for kind, listed in (('folder', inside), ('module', direct)):
        key = KINDS[kind]
        for name in listed:
            text = overlay[key].get(name) or (summary[key].get(name) or {}).get('text')
            items.append({'name': name, 'kind': kind, 'text': text.rstrip('\n') if text else None})
    return items


# ----------------------------------------------------------------------------- the summary and the files of the canon

def read_summary(instance):
    """canon/descriptions.json: {'modules': {name: {'text', 'revision', 'published', 'tested'}},
    'folders': {name: {..., 'boundary'}}, 'since': {module: sequence}}.

    `revision` of a description is the revision of the canon its text was written or confirmed against
    (apply_descriptions), and `published` is the sequence of the publication that last carried it, with a
    new text or with the same one (gather). `since` gives for each module of the structural index the
    sequence of the publication at which the module first stood in the index (gather).

    An instance that has no description yet has no such file, and it reads as an empty summary. A summary
    without `since` reads as one whose map is empty: the map has not been made yet."""
    path = Path(instance) / 'canon' / 'descriptions.json'
    data = read_json(path) if path.exists() else {}
    return {**{key: data.get(key, {}) for key in KINDS.values()}, 'since': data.get('since', {})}


def published_at(entry):
    """The sequence of the publication that last carried a description, from its entry in the summary.

    It has one use: a folder is not behind for a module that came with the publication that carried its
    description (due_text). An entry that does not say it, as one of a summary gathered before the summary
    kept it, counts as carried at its `revision`, which is no later than its publication: a module then
    stays listed where the true number would have cleared it, and none is cleared that should be listed."""
    return entry.get('published', entry['revision'])


def put(canon, kind, name, text, sequence, source):
    """Write one description into the canon. A text it replaces leaves its difference in the history.

    `source` is the ID of the publication. Doing it again after an interruption finds the text in place and
    writes nothing, or finds the old text still there and writes the same history entry and the same file."""
    target = description_file(canon.root, kind, name)
    if target.exists():
        old = target.read_text(encoding='utf-8')
        if old == text:
            return
        folder = canon.history / 'descriptions' / KINDS[kind] / Path(*name.split('.'))
        folder.mkdir(parents=True, exist_ok=True)
        diff = '\n'.join(difflib.unified_diff(text.splitlines(), old.splitlines(), 'current', 'replaced', lineterm=''))
        write_text(folder / f'{sequence:06d}.md',
                   f'# {name}: description of the {kind} replaced at revision {sequence} by {source}\n\n'
                   f'The current text is at `{target.relative_to(canon.root).as_posix()}`. The difference below '
                   f'turns the current text into the text that was replaced.\n\n```diff\n{diff}\n```\n')
    target.parent.mkdir(parents=True, exist_ok=True)
    write_text(target, text)


def apply_descriptions(canon, descriptions, results, index, sequence, source, against):
    """Put descriptions into the canon and say which were carried:
    {'modules': {name: {'revision', 'tested'}}, 'folders': {...}}.

    `descriptions` has the form of candidate_descriptions and `index` is the structural index after the
    publication. A description whose module or folder does not exist then is left out and is no error: the
    canon can have changed since the text was written. A description that is in the canon with the same
    text already is carried as well, which is how a description is confirmed. `results` are the results of
    the blind descent test that came with the texts, and a description is carried as tested when one of them,
    taken on its present text, passed. None stands for the publication of an operator, whose texts were
    tested before the command was given.

    `sequence` is the sequence of the publication, under which a replaced text goes to the history.
    `against` is the revision of the canon that the texts were written or confirmed against, which can be
    an earlier one: the revision at which a session last prepared its change, or the one the operator
    named. It is the number the command `index` shows, the sequence of the latest publication then. Each
    carried description takes it as its `revision`. A module that came to a folder after the folder's
    description was written and before the description was published then shows the folder as behind
    (due_text), which the sequence of the publication would hide, and a report made in that time stays
    listed against the description (open_reports)."""
    existing = {'module': set(index['modules']), 'folder': set(folders_of(index['modules']))}
    carried = {key: {} for key in KINDS.values()}
    for kind, key in KINDS.items():
        for name, text in sorted(descriptions[key].items()):
            if name not in existing[kind]:
                continue
            put(canon, kind, name, text, sequence, source)
            carried[key][name] = {'revision': against, 'tested': results is None or any(
                item.get('passed') is True for item in results_for(results, kind, name, text))}
    return carried


def gather(instance, index, sequence, carried, known):
    """The summary of the descriptions as the files of the canon hold them, for canon/descriptions.json.

    It is gathered where the summary of the records is: after the written part of a publication is in
    place, with the index the publication leaves. Every description file is read. A description that the
    publication carried (apply_descriptions) takes the revision and the `tested` value given there, and
    `sequence` as `published`: the publication that last carried it is this one. Every other keeps what
    the summary in place says of it. A file that no publication is known to have carried, which only a
    hand could have put there, counts as untested. A file whose module or folder no longer exists goes to
    the history as `<sequence>-removed.md`, so the summary holds an entry only for what exists in the
    index.

    `since` says for each module of the index at which publication it first stood there. A module that the
    map in place has keeps its sequence, a module that the map does not have takes `sequence`, and a module
    that has left the index leaves the map. A module that a rearrangement made out of elements the canon
    already had, or moved into another folder, is therefore new at this publication, as a module that
    brings new elements is. The map is first made by the first publication that leaves a description, and
    until then it is empty. It is then made from `known`, which gives for each module the sequence of the
    publication that added its first element, as the research stood before this publication
    (model['module_since'] of knowledge.replay); a module that this publication brings takes `sequence`.

    The caller writes the result, and it writes it before it puts the index of the publication in place
    (Runner.publish). Doing all of it again after an interruption then gives the same summary. The files
    moved to the history are no longer found, and `carried` is made again from the same publication. The
    map is either in place, and a repeat leaves it as it is, or it is not, and then the index in place,
    from which `known` is made, is still the one from before the publication."""
    canon = Canon(instance)
    previous = read_summary(instance)
    existing = {'module': set(index['modules']), 'folder': set(folders_of(index['modules']))}
    summary = {key: {} for key in KINDS.values()}
    base = previous['since'] or known
    summary['since'] = {module: base.get(module, sequence) for module in sorted(index['modules'])}
    for kind, key in KINDS.items():
        base = canon.root / 'descriptions' / key
        for name, path in described_files(canon.root, kind):
            if name not in existing[kind]:
                target = (canon.history / 'descriptions' / key / path.relative_to(base).with_suffix('')
                          / f'{sequence:06d}-removed.md')
                target.parent.mkdir(parents=True, exist_ok=True)
                replace_file(path, target)
                continue
            text = path.read_text(encoding='utf-8')
            if name in carried[key]:
                entry = {'revision': carried[key][name]['revision'], 'published': sequence,
                         'tested': bool(carried[key][name]['tested'])}
            elif name in previous[key]:
                entry = {'revision': previous[key][name]['revision'], 'published': published_at(previous[key][name]),
                         'tested': previous[key][name]['tested']}
            else:
                entry = {'revision': sequence, 'published': sequence, 'tested': False}
            entry['text'] = text.rstrip('\n')
            if kind == 'folder':
                entry['boundary'] = boundary_of(text)
            summary[key][name] = entry
    return summary


# ----------------------------------------------------------------------------- the listings of the descent

def plural(count, word):
    return f'{count} {word}' + ('' if count == 1 else 's')


def folder_item(name, counted, summary):
    """A folder in a listing: its counts on one line, and under it its description, each paragraph on one line."""
    modules, elements = counted[name]
    entry = summary['folders'].get(name)
    described = [one_line(part) for part in paragraphs(entry['text'])] if entry else [NO_DESCRIPTION]
    return [f"- {name} · {plural(modules, 'module')} · {plural(elements, 'element')}"] + ['  ' + line for line in described]


def module_said(name, modules, summary):
    """What a listing says of a module after its name: its number of elements and its line."""
    entry = summary['modules'].get(name)
    return f"{plural(len(modules[name]), 'element')} — " + (one_line(entry['text']) if entry else NO_LINE)


def module_item(name, modules, summary):
    """A module in a listing: its number of elements and its line, on one line."""
    return f'- {name} · ' + module_said(name, modules, summary)


def level_lines(modules, library, summary, parent_name):
    """The folders and the modules directly inside a folder, or directly under the library, and their number."""
    inside, direct = children(modules, library, parent_name)
    counted = counts(modules)
    lines = [f'Folders ({len(inside)})', '']
    for name in inside:
        lines += folder_item(name, counted, summary)
    if inside:
        lines.append('')
    lines += [f'Modules directly under {library} ({len(direct)})' if parent_name == library
              else f'Modules ({len(direct)})', '']
    lines += [module_item(name, modules, summary) for name in direct]
    if direct:
        lines.append('')
    return lines + [f"{plural(len(inside), 'folder')} and {plural(len(direct), 'module')} at this level."]


def folder_level(model, summary):
    """The top of the index: every folder directly under the library with its description and its counts, and
    the modules that lie directly under the library.

    The command `index` prints this text, knowledge/folders.md holds it (knowledge.render), and the starting
    context of a session carries it (context.assemble). The number of folders in its first line is that of
    the folders at this level, the ones the text lists."""
    modules = modules_of(model)
    library = model['library']
    top = children(modules, library, library)[0]
    head = (f"Index of the canon · revision {model['sequence']} · library {library}: {plural(len(top), 'folder')}, "
            f"{plural(len(modules), 'module')}, {plural(sum(len(names) for names in modules.values()), 'element')}.")
    return '\n'.join([head, ''] + level_lines(modules, library, summary, library))


def folder_listing(model, summary, name):
    """One folder: its description, the folders directly inside it and the modules directly inside it."""
    modules = modules_of(model)
    count = counts(modules)[name]
    entry = summary['folders'].get(name)
    return '\n'.join([f"{name} · folder · {plural(count[0], 'module')} · {plural(count[1], 'element')}", '',
                      entry['text'] if entry else '(no description yet)', '']
                     + level_lines(modules, model['library'], summary, name))


def module_listing(model, summary, name, head):
    """One module: its line and one line for each of its elements. `head` gives the line of an element
    (canon_tool.head), the form every listing of elements uses."""
    names = modules_of(model)[name]
    entry = summary['modules'].get(name)
    return '\n'.join([f"{name} · module · {plural(len(names), 'element')}", entry['text'] if entry else NO_LINE, '']
                     + [head(model['elements'][element]) for element in names]
                     + [plural(len(names), 'element') + '.'])


def index_text(model, summary, name, head):
    """What the command `index` prints: the folder level without a name, and otherwise the folder or the
    module of that name. A name that is both prints the module and then the folder. The name of the library
    is the top of the index and prints the folder level."""
    if name is None:
        return folder_level(model, summary)
    modules = modules_of(model)
    parts = []
    if name in modules:
        parts.append(module_listing(model, summary, name, head))
    if name in counts(modules):
        parts.append(folder_listing(model, summary, name))
    if name == model['library']:
        parts.append(folder_level(model, summary))
    if not parts:
        raise CanonError(f'no folder or module of the canon has the name {name}')
    return '\n\n'.join(parts)


# ----------------------------------------------------------------------------- what keeps the index current

def due_text(model, summary, kept=()):
    """What the index lacks and what has been reported about it, each as a complete counted list (`index --due`).

    It is written for the organizer and open to every session. A module's revision is the sequence of the
    publication at which it first stood in the index (`since` of the summary). A folder has fallen behind
    when a module beneath it, at any depth, came after the revision of its description, which is the
    revision of the canon the description was written or confirmed against, and did not come with the
    publication that carried that description: an organizer's change that brings a module into a folder
    and carries the folder's description wrote the description with that module before it. A module that
    was moved into the folder by another publication counts, and so does one that another change
    published while the description was being written. Where the summary has no entry for a module, as in
    a summary gathered before it kept the map, the module has the sequence of the publication that added
    its first element (model['module_since']).

    A report says that a description did not lead a session to an element. `kept` are the reports of the
    candidates that were not published (kept_reports). Each report is listed, with where it came from,
    until the description it names is written or confirmed against a revision of the canon that showed
    the report (open_reports), and its last line says from which revision that is and which revision the
    description has now. So a report leaves the list by the revision its description is given. An
    organizer's change gives it the revision of its preparation, at which `prepare` named the report to
    the session. The operator's publication (`describe`) gives it the revision of the canon at the command,
    or the one named with `--revision`, and takes a report off by that revision whether or not the operator
    read the list. A report also leaves when the module or folder it names is no longer in the canon, and
    a report kept of a failed publication when the candidate of the same review was published after all
    (kept_reports)."""
    modules = modules_of(model)
    counted = counts(modules)
    since = {module: summary['since'].get(module, model['module_since'].get(module, 0)) for module in modules}

    def folder_line(name):
        return f"- {name} · {plural(counted[name][0], 'module')} · {plural(counted[name][1], 'element')}"

    def section(title, rows):
        return [f'{title} ({len(rows)})', ''] + [line for row in rows for line in row] + ([''] if rows else [])

    behind = []
    for name in sorted(counted):
        entry = summary['folders'].get(name)
        newer = [module for module in modules
                 if entry and module.startswith(name + '.') and since[module] > entry['revision']
                 and since[module] != published_at(entry)]
        if newer:
            behind.append([f"- {name} · described at revision {entry['revision']} · "
                           f"{plural(len(newer), 'module')} since"]
                          + [f"  - {module} · revision {since[module]} · {module_said(module, modules, summary)}"
                             for module in newer])
    existing = {'modules': modules, 'folders': counted}
    untested = [[f"- {kind} {name} · revision {summary[key][name]['revision']}"]
                for kind, key in KINDS.items() for name in sorted(summary[key])
                if name in existing[key] and not summary[key][name]['tested']]
    reports = [[f"- {report['from']} · description {report['description']} · element {report['element']}",
                '  purpose: ' + one_line(report['purpose']),
                f"  listed until the description is written or confirmed against revision {report['needs']} or later; "
                + ('there is none yet' if report['has'] is None else f"it is of revision {report['has']}")]
               for report in open_reports(model, summary, kept)]
    boundaries = [[folder_line(name), f'  {BOUNDARY} ' + summary['folders'][name]['boundary']]
                  for name in sorted(counted) if (summary['folders'].get(name) or {}).get('boundary')]
    lines = [f"What the index of the canon lacks, and what has been reported about it · revision {model['sequence']}", '']
    lines += section('Modules without a line',
                     [[f"- {name} · {plural(len(modules[name]), 'element')}"] for name in modules
                      if name not in summary['modules']])
    lines += section('Folders without a description',
                     [[folder_line(name)] for name in sorted(counted) if name not in summary['folders']])
    lines += section('Folders that received modules after their description was last written or confirmed', behind)
    lines += section('Descriptions published without a blind descent test', untested)
    lines += section('Reports that a description did not lead a session to an element, each listed until its '
                     'description is written or confirmed against a revision of the canon that showed the report',
                     reports)
    lines += section('Folders whose description ends in a Boundary paragraph', boundaries)
    return '\n'.join(lines).rstrip('\n')
