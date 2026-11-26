"""The dependency map of a research instance, drawn from its canon by script.

    python depmap.py <instance> --out <folder> [--all]
    python depmap.py <folder>/dependency_map.json --out <folder>     draw again, without the instance

The map is a view. It is computed from the model that knowledge.replay derives from the structural
index, the records and the published verdicts; nothing is extracted by hand and nothing is stored
in the instance. The command writes three files into the output folder:

    dependency_map.json   the semantic data: units, edges, groups, and the folded elements edges pass through
    dependency_map.svg    the drawing
    dependency_map.html   the same drawing in a page that zooms, finds a unit or a folded step by name, follows a
                          unit up and down, and shows its details

The drawing is laid out by code that ships with the skill and needs nothing beyond Python.
depmap/draw.py describes the layout.

How the map is derived. The words are those of docs/do-math/lean-canon-design.md, sections 4.4, 5 and 13.1.

Items. The map works per statement, as the standing does. A declaration whose record says it is
another proof of a statement (`proves:`, confirmed by Lean) is read as that statement wherever a
proof names it. An item is therefore a statement (a theorem that is not another proof of something)
or a declaration that is not a theorem (a definition, an inductive type, an opaque constant).

Units. An item is a unit when its record gives `weight: unit`; the root is always one. By default
the map shows the units the proof of the root rests on: starting at the root, everything that any
proof of a reached statement names, everything a reached statement or definition mentions, and so
on. With `--all` it shows every unit of the canon. Every other item is folded.

A refuted root. A research can end with the root refuted: a statement that Lean confirmed as the
negation of the root is settled. The result of that research is the refutation, so the map shows
it. The root's card says that the root is refuted, each settled refutation is a unit whatever its
weight, the default scope starts from the refutations as well as from the root, and so the map
shows what the refutation rests on.

Edges. An edge runs from what is used to what uses it, and there is at most one for a pair.
    direct       the proof of the target names the source (for a definition: its body does)
    contracted   the proof reaches the source only through folded items; `via` lists every folded
                 item on some such path, and the drawing writes them on the line
    mention      the statement of the target mentions the source, itself or through folded definitions
    alternative  the source is another proof of the target statement; the two proofs are separate arguments, not joint inputs
    refutation   the source is a statement whose record says that it refutes the root and that Lean
                 confirmed as the root's negation; the root is refuted once that statement is settled
A folded item passes on everything it rests on: what each of its proofs names and what its
statement mentions. A pair related in both ways gets the relation that says more about it: a
definition that the statement mentions is a `mention` whatever the proof does with it, and a
statement that the proof uses is a proof edge. The edge keeps both relations in full under `proof`
and `statement`, each with whether it is direct and every folded item it passes through, so a
folded element stays traceable by name even where the line does not carry it. A declaration's
reference to its own statement is not an edge.

Alternatives. Another proof of a unit statement is drawn as a card of its own, joined to the
statement by an `alternative` edge, and what that proof names enters the proof's card and not the
statement's, so that two complete proofs of one goal are not read as joint inputs. Another proof of
a folded statement is folded with it. Alternatives can close a cycle (a later proof of S may rest on
a result that uses S), so the map is not assumed to be acyclic.

Each unit carries its Lean name as the stable identifier, a label (its short name, or the last
component of the Lean name), its kind, and for a statement the standing of its own proof, whether
the statement is settled through any of its proofs, and whether one of its proofs is complete in
Lean from the allowed axioms. A proof card carries the same three for that proof. Units are
grouped by the folder of their module, that is, the module name without its last component.
"""
import argparse
import importlib.util
from pathlib import Path
import sys

from canon import name_parts

HERE = Path(__file__).resolve().parent
SCHEMA = 1
FILES = {'data': 'dependency_map.json', 'svg': 'dependency_map.svg', 'html': 'dependency_map.html'}


def drawing():
    """The drawing code beside this file. It reads the map's JSON and nothing of the runtime."""
    name = 'depmap_draw'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, HERE / 'depmap' / 'draw.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def folder_of(module):
    """The folder of a module: its name without the last component. A top-level module is its own folder."""
    return module.rsplit('.', 1)[0] if '.' in module else module


def derive(model, everything=False):
    """The semantic map of a replayed model: units, edges, groups and the folded elements edges pass through.

    The result holds no coordinates. With the statement in natural language that from_instance adds to
    each unit from its record, it is the whole input of the drawing."""
    elements = model['elements']

    def theorem(name):
        return elements[name]['kind'] == 'theorem'

    def item(name):
        return elements[name]['statement_of'] if theorem(name) else name

    def declarations(name):
        return elements[name]['proofs'] if theorem(name) else [name]

    def named(declaration, key):
        """The items a declaration names in its proof (`uses`) or mentions in its statement (`statement_uses`)."""
        own, found = item(declaration), []
        for used in elements[declaration][key]:
            if used in elements and item(used) != own and item(used) not in found:
                found.append(item(used))
        return found

    brought = {}

    def brings(name):
        """Everything an item rests on: what each of its proofs names and what its statement mentions."""
        if name not in brought:
            found = {}
            for declaration in declarations(name):
                for key in ('uses', 'statement_uses'):
                    found.update(dict.fromkeys(named(declaration, key)))
            brought[name] = list(found)
        return brought[name]

    def order(names):
        return sorted(names, key=lambda n: (elements[n]['module'], n))

    root = item(model['root'])
    # The statements that refute the root, and among them those that are settled. A settled one is the
    # result of the research, so it is drawn whatever weight its record gives it.
    refuting = order({item(name) for name, element in elements.items()
                      if theorem(name) and element.get('refutes') and item(element['refutes']) == root})
    settled_refuting = [name for name in refuting if any(elements[p]['settled'] for p in elements[name]['proofs'])]

    def is_unit(name):
        return name == root or elements[name]['weight'] == 'unit' or name in settled_refuting

    def reach(start, through):
        """The items reached from `start`, continuing only through the items `through` accepts."""
        seen, pending = {}, list(start)
        while pending:
            name = pending.pop()
            if name in seen:
                continue
            seen[name] = True
            if through(name):
                pending += brings(name)
        return list(seen)

    items = order(name for name in elements if item(name) == name)
    scope = set(items) if everything else set(reach([root] + settled_refuting, lambda name: True))
    shown = [name for name in items if is_unit(name) and name in scope]

    users = {}
    for name in items:
        if not is_unit(name):
            for used in brings(name):
                users.setdefault(used, []).append(name)
    leads = {}

    def leading(unit):
        """The folded items from which a unit is reached through folded items alone."""
        if unit not in leads:
            seen, pending = set(), list(users.get(unit, ()))
            while pending:
                name = pending.pop()
                if name not in seen:
                    seen.add(name)
                    pending += users.get(name, ())
            leads[unit] = seen
        return leads[unit]

    def relation(start, own):
        """The units a list of items leads to: named directly, or through the folded items listed in `via`.

        A folded item is on a path to a unit when it is reached from `start` and the unit is reached from it."""
        found = {x: {'direct': True, 'via': set()} for x in start if is_unit(x)}
        passed = reach([x for x in start if not is_unit(x)], lambda x: not is_unit(x))
        folded = {x for x in passed if not is_unit(x)}
        for unit in passed:
            if unit not in folded:
                found.setdefault(unit, {'direct': False, 'via': set()})['via'] = folded & leading(unit)
        found.pop(own, None)
        return found

    edges, folded_names = [], set()

    def join(target, declaration, with_statement):
        own = item(declaration)
        proof = relation(named(declaration, 'uses'), own)
        statement = relation(named(declaration, 'statement_uses'), own) if with_statement else {}
        for source in order(set(proof) | set(statement)):
            by_proof = source in proof and (theorem(source) or source not in statement)
            found = proof[source] if by_proof else statement[source]
            sides = {}
            for key, side in (('proof', proof.get(source)), ('statement', statement.get(source))):
                sides[key] = {'direct': side['direct'], 'via': order(side['via'])} if side else None
                folded_names.update(side['via'] if side else ())
            edges.append({'source': source, 'target': target,
                          'kind': 'mention' if not by_proof else 'direct' if found['direct'] else 'contracted',
                          'via': [] if found['direct'] else order(found['via']), **sides})

    units = []

    def card(name, role):
        element = elements[name]
        unit = {'id': name, 'label': element['short'] or name_parts(name)[-1], 'role': role, 'kind': element['kind'],
                'module': element['module'], 'group': folder_of(element['module']), 'root': name == root,
                'description': element['description'], 'lean': element['statement']}
        if role == 'proof':
            unit['proves'] = item(name)
        if name == root and theorem(name):
            unit['refuted'] = bool(element['refuted_by'])
        if name in refuting:
            unit['refutes'] = root
        if theorem(name):
            proofs = element['proofs'] if role == 'statement' else [name]
            unit.update(standing=element['standing'],
                        settled=element['statement_settled'] if role == 'statement' else element['settled'],
                        formal=any(elements[p]['formal'] for p in proofs))
        if element.get('source'):
            unit['source'] = element['source']
        units.append(unit)

    for name in shown:
        card(name, 'statement' if theorem(name) else 'definition')
        join(name, name, True)
        for proof in declarations(name)[1:]:
            card(proof, 'proof')
            join(proof, proof, False)
            edges.append({'source': proof, 'target': name, 'kind': 'alternative', 'via': [],
                          'proof': None, 'statement': None})
    for name in refuting:
        if name in shown:
            edges.append({'source': name, 'target': root, 'kind': 'refutation', 'via': [],
                          'proof': None, 'statement': None})

    groups = {}
    for unit in units:
        groups.setdefault(unit['group'], []).append(unit['id'])
    root_element = elements[root]
    return {'schema': SCHEMA, 'title': 'Dependency map of ' + root,
            'root': root, 'root_label': root_element['short'] or name_parts(root)[-1],
            'root_state': model.get('root_state'), 'library': model.get('library'),
            'revision': model.get('revision'), 'sequence': model.get('sequence'),
            'scope': 'all' if everything else 'root',
            'units': units, 'edges': edges,
            'groups': [{'id': key, 'label': key, 'units': groups[key]} for key in sorted(groups)],
            'folded': {name: {'label': elements[name]['short'] or name_parts(name)[-1], 'kind': elements[name]['kind'],
                              'description': elements[name]['description']} for name in order(folded_names)},
            'counts': {'elements': len(elements), 'units': len(units), 'edges': len(edges), 'groups': len(groups)}}


def from_instance(instance, everything=False):
    """The map of an instance as it stands now. Reads the canon and the published events; writes nothing.

    Every unit of the map carries the statement in natural language that its record gives, where it gives one."""
    from canon import Canon, read_record
    from knowledge import replay
    data = derive(replay(instance), everything)
    canon = Canon(instance)
    for unit in data['units']:
        record = read_record(canon, unit['id'])
        words = (record['sections'].get('Statement') or '').strip() if record else ''
        if words:
            unit['statement'] = words
    return data


def write(data, out):
    """Write the map's data and its two drawings into a folder; returns what was written."""
    from runtime_support import write_json, write_text
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    draw = drawing()
    svg, page = draw.render(data)
    write_json(out / FILES['data'], data)
    write_text(out / FILES['svg'], svg)
    write_text(out / FILES['html'], page)
    return {'files': {key: str(out / name) for key, name in FILES.items()}}


def say(text, stream=None):
    """Print a line; a character the console cannot show is written as an escape instead of ending the command."""
    stream = stream or sys.stdout
    encoding = getattr(stream, 'encoding', None) or 'ascii'
    print(text.encode(encoding, 'backslashreplace').decode(encoding), file=stream)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Draw the dependency map of a research instance from its canon.')
    parser.add_argument('source', help='an instance folder, or a dependency_map.json to draw again')
    parser.add_argument('--out', required=True, help='the folder the map is written into')
    parser.add_argument('--all', action='store_true', help='every unit of the canon, not only what the proof of the root rests on')
    args = parser.parse_args(argv)
    source = Path(args.source)
    try:
        if source.is_file():
            from runtime_support import read_json
            data = read_json(source)
            if not isinstance(data, dict) or data.get('schema') != SCHEMA or not isinstance(data.get('units'), list):
                raise ValueError(f'{source} is not a dependency map written by this command')
            # A file that was changed after the command wrote it can keep a line whose unit it no longer holds.
            # The drawing needs both ends of every line, so the file is refused here, with the name that is missing.
            units = {unit['id'] for unit in data['units']}
            stray = sorted({edge[end] for edge in data['edges'] for end in ('source', 'target')} - units)
            if stray:
                raise ValueError(f'{source} has a line to or from {stray[0]}, which is not among its units')
            if args.all:
                raise ValueError('--all needs the instance; a map drawn again keeps the scope it was derived with')
        elif (source / 'instance.json').is_file():
            data = from_instance(source, args.all)
        else:
            raise ValueError(f'{source} is neither an instance folder nor a dependency_map.json')
        result = write(data, args.out)
    except (ValueError, OSError) as error:
        say('depmap: ' + str(error), sys.stderr)
        return 2
    counts = data['counts']
    say(f"{counts['units']} units, {counts['edges']} edges, {counts['groups']} groups; "
        f"{len(data['folded'])} folded elements on edges; scope: {drawing().scope_words(data)}")
    for path in result['files'].values():
        say(path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
