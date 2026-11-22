"""The dependency map: which elements are units, how steps fold into edges, alternatives, and the drawing.

The derivation tests work on small hand-made canons. Each is written as the files replay reads (the
structural index, the summary of the records, one published change with review's verdicts), and the
model comes from the real replay, so the tests hold the map to the model the runtime computes. The
last class draws the map of an instance published through the real path.
"""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import depmap
from knowledge import replay
from runtime_support import read_json, write_json
from settings import defaults
from support import ScenarioCase

draw = depmap.drawing()
SVG = '{http://www.w3.org/2000/svg}'


def statement(name, weight='step', uses=(), mentions=(), module='Lib.Main', short=None, proves=None,
              proof='informal', standing='accepted', refutes=None):
    """A theorem of a hand-made canon. proof: None, 'informal' (written, Lean ends in sorry) or 'formal'."""
    return {'name': name, 'kind': 'theorem', 'weight': weight, 'uses': list(uses), 'mentions': list(mentions),
            'module': module, 'short': short, 'proves': proves, 'proof': proof, 'standing': standing, 'refutes': refutes}


def definition(name, weight='step', uses=(), mentions=(), module='Lib.Defs', short=None, kind='def'):
    return {'name': name, 'kind': kind, 'weight': weight, 'uses': list(uses), 'mentions': list(mentions),
            'module': module, 'short': short, 'proves': None, 'proof': 'formal', 'standing': None}


def write_canon(folder, rows, root='Lib.root'):
    """The files replay reads, for a canon given as rows; every proof receives the verdict its row names."""
    folder = Path(folder)
    entries, records, verdicts = {}, {}, []
    for row in rows:
        name, theorem = row['name'], row['kind'] == 'theorem'
        formal = row['proof'] == 'formal'
        entries[name] = {'name': name, 'kind': row['kind'], 'module': row['module'], 'file': row['module'].replace('.', '/') + '.lean',
                         'span': [1, 0, 2, 0], 'statement': name + ' : stated in Lean', 'statement_hash': 'hash-of-' + name,
                         'prop': theorem, 'statement_uses': row['mentions'], 'uses': row['uses'], 'library': [],
                         'direct_axioms': [] if formal else ['sorryAx'], 'lean_proof': 'complete' if formal else 'sorry'}
        records[name] = {'weight': row['weight'], 'short': row['short'], 'proves': row['proves'], 'refutes': row.get('refutes'),
                         'source': None, 'description': 'What ' + name + ' is.', 'proof': row['proof'] == 'informal',
                         'statement': False, 'approaches': [], 'path': 'records/' + name.replace('.', '/') + '.md'}
        if theorem and row['proof']:
            verdicts.append({'element': name, 'correct': 'not_confirmed' if row['standing'] == 'not_confirmed' else 'confirmed',
                             'accepted': row['standing'] == 'accepted', 'reason': 'Read by review.'})
        elif theorem:
            verdicts.append({'element': name, 'correct': 'not_applicable', 'accepted': False, 'reason': 'Stated faithfully.'})
    pairs = {f"same|{row['name']}|{row['proves']}": True for row in rows if row['proves']}
    pairs.update({f"negation|{row['name']}|{row['refutes']}": True for row in rows if row.get('refutes')})
    for part in ('canon', 'knowledge/events', 'knowledge/changes/c1'):
        (folder / part).mkdir(parents=True, exist_ok=True)
    write_json(folder / 'instance.json', {'schema': 2, 'root': root, 'library': 'Lib'})
    write_json(folder / 'settings.json', defaults())
    write_json(folder / 'canon/index.json', {'revision': 1, 'modules': {}, 'entries': entries, 'aux': {}, 'pairs': pairs})
    write_json(folder / 'canon/records.json', records)
    write_json(folder / 'knowledge/events/c1.json', {'id': 'c1', 'sequence': 1, 'kind': 'change', 'folder': 'changes/c1',
                                                     'producer_role': 'attempt'})
    change = folder / 'knowledge/changes/c1'
    write_json(change / 'applied.json', {'added': [row['name'] for row in rows], 'replaced': [], 'records': []})
    write_json(change / 'assessment.json', {'publish': True, 'contribution': 'The canon of the test.', 'elements': verdicts})
    write_json(change / 'change.json', {'title': 'The canon', 'description': 'A hand-made canon.'})
    return folder


class MapCase(unittest.TestCase):
    def map(self, rows, everything=False, root='Lib.root'):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        return depmap.derive(replay(write_canon(temp.name, rows, root)), everything)

    @staticmethod
    def ids(data):
        return [unit['id'] for unit in data['units']]

    @staticmethod
    def unit(data, name):
        return next(unit for unit in data['units'] if unit['id'] == name)

    @staticmethod
    def edge(data, source, target):
        found = [edge for edge in data['edges'] if (edge['source'], edge['target']) == (source, target)]
        assert len(found) <= 1, found
        return found[0] if found else None


class Derivation(MapCase):
    def test_units_are_the_unit_weight_elements_the_root_rests_on(self):
        rows = [statement('Lib.root', 'unit', uses=['Lib.a', 'Lib.s']), statement('Lib.a', 'unit'),
                statement('Lib.s'), statement('Lib.stray', 'unit'), statement('Lib.strayStep', uses=['Lib.a'])]
        data = self.map(rows)
        self.assertEqual(self.ids(data), ['Lib.a', 'Lib.root'])
        self.assertEqual(data['scope'], 'root')
        self.assertEqual(data['counts'], {'elements': 5, 'units': 2, 'edges': 1, 'groups': 1})
        everything = self.map(rows, everything=True)
        self.assertEqual(self.ids(everything), ['Lib.a', 'Lib.root', 'Lib.stray'])
        self.assertEqual(everything['scope'], 'all')

    def test_the_root_is_a_unit_whatever_its_record_says(self):
        data = self.map([statement('Lib.root', 'step', uses=['Lib.a']), statement('Lib.a', 'unit')])
        self.assertEqual(self.ids(data), ['Lib.a', 'Lib.root'])
        self.assertTrue(self.unit(data, 'Lib.root')['root'])
        self.assertEqual(self.edge(data, 'Lib.a', 'Lib.root')['kind'], 'direct')

    def test_a_step_is_folded_into_the_edge_that_passes_through_it(self):
        data = self.map([statement('Lib.root', 'unit', uses=['Lib.s2']), statement('Lib.s2', uses=['Lib.s1', 'Lib.b']),
                         statement('Lib.s1', uses=['Lib.a']), statement('Lib.a', 'unit'), statement('Lib.b', 'unit')])
        self.assertEqual(self.ids(data), ['Lib.a', 'Lib.b', 'Lib.root'])
        through_two = self.edge(data, 'Lib.a', 'Lib.root')
        self.assertEqual((through_two['kind'], through_two['via']), ('contracted', ['Lib.s1', 'Lib.s2']))
        self.assertEqual(through_two['proof'], {'direct': False, 'via': ['Lib.s1', 'Lib.s2']})
        self.assertIsNone(through_two['statement'])
        through_one = self.edge(data, 'Lib.b', 'Lib.root')
        self.assertEqual((through_one['kind'], through_one['via']), ('contracted', ['Lib.s2']))
        # No edge is drawn between the two units below: neither proof names the other.
        self.assertIsNone(self.edge(data, 'Lib.a', 'Lib.b'))
        self.assertEqual(sorted(data['folded']), ['Lib.s1', 'Lib.s2'])
        self.assertEqual(data['folded']['Lib.s1']['label'], 's1')

    def test_a_direct_use_stays_direct_and_keeps_the_folded_paths(self):
        data = self.map([statement('Lib.root', 'unit', uses=['Lib.a', 'Lib.s']), statement('Lib.s', uses=['Lib.a']),
                         statement('Lib.a', 'unit')])
        edge = self.edge(data, 'Lib.a', 'Lib.root')
        self.assertEqual((edge['kind'], edge['via']), ('direct', []))
        self.assertEqual(edge['proof'], {'direct': True, 'via': ['Lib.s']})

    def test_an_edge_stops_at_the_first_unit_on_a_path(self):
        data = self.map([statement('Lib.root', 'unit', uses=['Lib.a']), statement('Lib.a', 'unit', uses=['Lib.s']),
                         statement('Lib.s', uses=['Lib.b']), statement('Lib.b', 'unit')])
        self.assertEqual(self.edge(data, 'Lib.a', 'Lib.root')['kind'], 'direct')
        self.assertEqual(self.edge(data, 'Lib.b', 'Lib.a')['via'], ['Lib.s'])
        self.assertIsNone(self.edge(data, 'Lib.b', 'Lib.root'))

    def test_a_refuted_root_is_shown_as_refuted_with_the_refutation_and_what_it_rests_on(self):
        # The root has no proof. A statement that Lean confirmed as its negation is settled through a lemma.
        # The refutation is a step by its record and is drawn all the same, because it is the result.
        rows = [statement('Lib.root', 'unit', proof=None), statement('Lib.lemma', 'unit'),
                statement('Lib.notRoot', 'step', uses=['Lib.lemma'], refutes='Lib.root', module='Lib.Against'),
                statement('Lib.stray', 'unit')]
        data = self.map(rows)
        self.assertEqual(self.ids(data), ['Lib.notRoot', 'Lib.lemma', 'Lib.root'])
        root, against = self.unit(data, 'Lib.root'), self.unit(data, 'Lib.notRoot')
        self.assertEqual((root['refuted'], root['settled'], against['refutes'], against['settled']),
                         (True, False, 'Lib.root', True))
        self.assertEqual(self.edge(data, 'Lib.notRoot', 'Lib.root')['kind'], 'refutation')
        self.assertEqual(self.edge(data, 'Lib.lemma', 'Lib.notRoot')['kind'], 'direct')
        self.assertEqual(data['root_state'], 'informal_refuted')
        self.assertIn('refuted', draw.status_of(root))
        self.assertIn('refutes the root', draw.status_of(against))
        # A refutation that is not settled refutes nothing yet: the root is not marked, and the default map does
        # not start from it. With every unit in scope its card and its line are drawn when it is a unit.
        open_rows = [statement('Lib.root', 'unit', proof=None),
                     statement('Lib.notRoot', 'unit', refutes='Lib.root', proof=None, module='Lib.Against')]
        data = self.map(open_rows)
        self.assertEqual((self.ids(data), self.unit(data, 'Lib.root')['refuted']), (['Lib.root'], False))
        data = self.map(open_rows, everything=True)
        self.assertEqual(self.edge(data, 'Lib.notRoot', 'Lib.root')['kind'], 'refutation')
        # The refutation line is drawn like every other line.
        svg, page, engine, note = draw.render(self.map(rows), 'layered', None)
        self.assertIn('refutes the root', svg)

    def test_another_proof_is_an_alternative_of_its_statement(self):
        data = self.map([statement('Lib.root', 'unit', uses=['Lib.a'], standing='held'),
                         statement('Lib.a', 'unit'), statement('Lib.b', 'unit'),
                         statement('Lib.rootAgain', 'step', uses=['Lib.b'], proves='Lib.root', module='Lib.Later')])
        self.assertEqual(self.ids(data), ['Lib.a', 'Lib.b', 'Lib.root', 'Lib.rootAgain'])
        other = self.unit(data, 'Lib.rootAgain')
        self.assertEqual((other['role'], other['proves'], other['root']), ('proof', 'Lib.root', False))
        self.assertEqual(self.edge(data, 'Lib.rootAgain', 'Lib.root')['kind'], 'alternative')
        # What each proof names enters that proof's card, so the two proofs are not read as joint inputs.
        self.assertEqual(self.edge(data, 'Lib.b', 'Lib.rootAgain')['kind'], 'direct')
        self.assertIsNone(self.edge(data, 'Lib.b', 'Lib.root'))
        self.assertIsNone(self.edge(data, 'Lib.a', 'Lib.rootAgain'))
        # The statement is settled through the accepted proof although its own proof is held back.
        root = self.unit(data, 'Lib.root')
        self.assertEqual((root['standing'], root['settled']), ('held', True))
        self.assertEqual((other['standing'], other['settled']), ('accepted', True))

    def test_a_proof_named_by_another_proof_is_read_as_its_statement(self):
        data = self.map([statement('Lib.root', 'unit', uses=['Lib.aAgain']), statement('Lib.a', 'unit', proof=None),
                         statement('Lib.aAgain', 'unit', proves='Lib.a', module='Lib.Later')])
        self.assertEqual(self.edge(data, 'Lib.a', 'Lib.root')['kind'], 'direct')
        self.assertIsNone(self.edge(data, 'Lib.aAgain', 'Lib.root'))
        self.assertEqual(self.edge(data, 'Lib.aAgain', 'Lib.a')['kind'], 'alternative')

    def test_another_proof_of_a_folded_statement_is_folded_with_it(self):
        data = self.map([statement('Lib.root', 'unit', uses=['Lib.s']), statement('Lib.s', uses=['Lib.a']),
                         statement('Lib.sAgain', 'unit', uses=['Lib.b'], proves='Lib.s', module='Lib.Later'),
                         statement('Lib.a', 'unit'), statement('Lib.b', 'unit')])
        self.assertEqual(self.ids(data), ['Lib.a', 'Lib.b', 'Lib.root'])
        for source in ('Lib.a', 'Lib.b'):
            self.assertEqual(self.edge(data, source, 'Lib.root')['via'], ['Lib.s'])

    def test_a_definition_that_is_a_unit_appears_with_the_statements_that_mention_it(self):
        data = self.map([
            statement('Lib.root', 'unit', uses=['Lib.a', 'Lib.tool'], mentions=['Lib.object']),
            statement('Lib.a', 'unit', mentions=['Lib.derived']),
            definition('Lib.object', 'unit', short='the object'),
            definition('Lib.derived', 'step', uses=['Lib.object']),
            definition('Lib.tool', 'unit'), definition('Lib.unused', 'unit'), definition('Lib.helper', 'step')])
        self.assertEqual(self.ids(data), ['Lib.object', 'Lib.tool', 'Lib.a', 'Lib.root'])
        self.assertEqual(self.unit(data, 'Lib.object')['role'], 'definition')
        self.assertNotIn('standing', self.unit(data, 'Lib.object'))
        mention = self.edge(data, 'Lib.object', 'Lib.root')
        self.assertEqual((mention['kind'], mention['via'], mention['statement']), ('mention', [], {'direct': True, 'via': []}))
        through = self.edge(data, 'Lib.object', 'Lib.a')
        self.assertEqual((through['kind'], through['via']), ('mention', ['Lib.derived']))
        # A definition that only the proof uses is a proof edge.
        self.assertEqual(self.edge(data, 'Lib.tool', 'Lib.root')['kind'], 'direct')

    def test_a_definition_stays_a_mention_when_the_proof_also_uses_it(self):
        data = self.map([statement('Lib.root', 'unit', uses=['Lib.object', 'Lib.s'], mentions=['Lib.object']),
                         statement('Lib.s', mentions=['Lib.object']), definition('Lib.object', 'unit')])
        edge = self.edge(data, 'Lib.object', 'Lib.root')
        self.assertEqual(edge['kind'], 'mention')
        self.assertEqual(edge['proof'], {'direct': True, 'via': ['Lib.s']})

    def test_alternatives_can_close_a_cycle_and_the_map_is_still_drawn(self):
        data = self.map([statement('Lib.root', 'unit', uses=['Lib.t']),
                         statement('Lib.s', 'unit', proof=None),
                         statement('Lib.t', 'unit', uses=['Lib.s']),
                         statement('Lib.sAgain', 'unit', uses=['Lib.t'], proves='Lib.s', module='Lib.Later')])
        self.assertEqual(self.edge(data, 'Lib.s', 'Lib.t')['kind'], 'direct')
        self.assertEqual(self.edge(data, 'Lib.t', 'Lib.sAgain')['kind'], 'direct')
        self.assertEqual(self.edge(data, 'Lib.sAgain', 'Lib.s')['kind'], 'alternative')
        # Neither statement settles the other, and the layout does not need an acyclic map.
        self.assertFalse(self.unit(data, 'Lib.s')['settled'])
        svg = draw.render(data, 'layered')[0]
        self.assertEqual(len(ElementTree.fromstring(svg).findall(f".//{SVG}g[@class='edge']")), len(data['edges']))

    def test_a_unit_carries_its_label_its_lean_name_its_kind_and_its_standing(self):
        data = self.map([
            statement('Lib.root', 'unit', uses=['Lib.held', 'Lib.open', 'Lib.gap', 'Lib.formal'], short='the main theorem',
                      mentions=['Lib.Shape']),
            statement('Lib.held', 'unit', standing='held'), statement('Lib.open', 'unit', proof=None),
            statement('Lib.gap', 'unit', standing='not_confirmed'), statement('Lib.formal', 'unit', proof='formal'),
            definition('Lib.Shape', 'unit', kind='inductive')])
        root = self.unit(data, 'Lib.root')
        self.assertEqual((root['id'], root['label'], root['kind'], root['role']),
                         ('Lib.root', 'the main theorem', 'theorem', 'statement'))
        self.assertEqual(self.unit(data, 'Lib.held')['label'], 'held')  # the last component of the Lean name
        self.assertEqual(self.unit(data, 'Lib.Shape')['kind'], 'inductive')
        found = {name.rsplit('.', 1)[1]: (unit.get('standing'), unit.get('settled'), unit.get('formal'))
                 for name, unit in ((u['id'], u) for u in data['units'])}
        self.assertEqual(found, {'root': ('accepted', False, False), 'held': ('held', False, False),
                                 'open': ('no_proof', False, False), 'gap': ('not_confirmed', False, False),
                                 'formal': ('accepted', True, True), 'Shape': (None, None, None)})
        self.assertEqual(depmap.last_component('Lib.«a.b»'), 'a.b')

    def test_units_are_grouped_by_the_folder_of_their_module(self):
        data = self.map([statement('Lib.root', 'unit', uses=['Lib.a', 'Lib.b'], module='Lib.Root'),
                         statement('Lib.a', 'unit', module='Lib.Columns.Basic'),
                         statement('Lib.b', 'unit', module='Lib.Columns.Signs'),
                         statement('Lib.c', 'unit', module='Lib.Unused.One')])
        self.assertEqual(data['groups'], [{'id': 'Lib', 'label': 'Lib', 'units': ['Lib.root']},
                                          {'id': 'Lib.Columns', 'label': 'Lib.Columns', 'units': ['Lib.a', 'Lib.b']}])
        self.assertEqual(self.unit(data, 'Lib.a')['group'], 'Lib.Columns')
        self.assertEqual(depmap.folder_of('Lib'), 'Lib')


def wide_canon():
    """Three groups, nine units over four layers, steps, a definition, and a second proof of the root."""
    return [
        definition('Lib.object', 'unit', short='the object <of> "study" & more'),
        statement('Lib.count', 'unit', mentions=['Lib.object'], module='Lib.Counting.Basic'),
        statement('Lib.bound', 'unit', uses=['Lib.count', 'Lib.glue'], mentions=['Lib.object'], module='Lib.Counting.Bounds'),
        statement('Lib.glue', uses=['Lib.sign']), statement('Lib.sign', 'unit', module='Lib.Signs.Basic', proof=None),
        statement('Lib.column', 'unit', uses=['Lib.sign', 'Lib.count'], module='Lib.Signs.Columns', standing='held'),
        statement('Lib.mono', 'unit', uses=['Lib.bound', 'Lib.column'], module='Lib.Signs.Columns', standing='not_confirmed'),
        statement('Lib.diag', 'unit', uses=['Lib.count'], module='Lib.Signs.Diagonal', proof='formal'),
        statement('Lib.root', 'unit', uses=['Lib.mono', 'Lib.column'], mentions=['Lib.object'], short='every row is unimodal'),
        statement('Lib.rootByDiagonal', 'unit', uses=['Lib.column', 'Lib.diag'], proves='Lib.root', module='Lib.Ways'),
    ]


class Drawing(MapCase):
    def test_every_unit_and_edge_is_drawn_and_marked_for_the_page(self):
        data = self.map(wide_canon())
        svg, page, engine, note = draw.render(data, 'layered')
        self.assertEqual((engine, note), ('layered', None))
        tree = ElementTree.fromstring(svg)  # well formed although a label carries <, " and &
        nodes = tree.findall(f".//{SVG}g[@class='node']")
        self.assertEqual(sorted(node.get('data-node') for node in nodes), sorted(self.ids(data)))
        edges = tree.findall(f".//{SVG}g[@class='edge']")
        self.assertEqual(sorted((edge.get('data-source'), edge.get('data-target'), edge.get('data-kind')) for edge in edges),
                         sorted((edge['source'], edge['target'], edge['kind']) for edge in data['edges']))
        self.assertEqual(len({edge.get('id') for edge in edges}), len(data['edges']))
        texts = [''.join(element.itertext()) for element in tree.iter(f'{SVG}text')]
        self.assertIn('every row is unimodal', texts)
        self.assertIn('Lib.rootByDiagonal', texts)
        self.assertIn('via glue', texts)
        said = {unit['id']: draw.status_of(unit) for unit in data['units']}
        self.assertEqual(said['Lib.root'], ['root', 'statement', 'accepted', 'not settled'])
        self.assertEqual(said['Lib.rootByDiagonal'], ['another proof', 'accepted', 'not settled'])
        # Complete in Lean, but resting on a statement whose proof ends in sorry: settled and not formal.
        self.assertEqual(said['Lib.diag'], ['statement', 'accepted', 'settled'])
        self.assertEqual(said['Lib.sign'], ['statement', 'no proof', 'not settled'])
        self.assertEqual(said['Lib.object'], ['definition'])
        for unit in data['units']:
            for line in draw.card_of(unit)['status']:
                self.assertIn(line, texts)
        self.assertEqual(sorted(group.get('data-group') for group in tree.findall(f".//{SVG}g[@class='group']")),
                         ['Lib', 'Lib.Counting', 'Lib.Signs'])
        # The page holds the same drawing and the data its panel reads.
        self.assertIn(svg, page)
        payload = page.split('<script type="application/json" id="map-data">', 1)[1].split('</script>', 1)[0]
        self.assertEqual(json.loads(payload), data)

    def test_cards_do_not_overlap_and_stand_inside_their_groups(self):
        data = self.map(wide_canon())
        cards = {unit['id']: draw.card_of(unit) for unit in data['units']}
        geometry = draw.layered(data, cards)
        boxes = list(geometry['cards'].items())
        for index, (first, a) in enumerate(boxes):
            for second, b in boxes[index + 1:]:
                self.assertFalse(draw.overlap(a, b), (first, second))
        for unit in data['units']:
            x, y, w, h = geometry['cards'][unit['id']]
            gx, gy, gw, gh = geometry['groups'][unit['group']]
            self.assertTrue(gx < x and gy < y and x + w < gx + gw and y + h < gy + gh, unit['id'])
        frames = list(geometry['groups'].values())
        for index, a in enumerate(frames):
            for b in frames[index + 1:]:
                self.assertFalse(draw.overlap(a, b))
        # An edge runs from the side of its source to the side of its target, and a used unit stands to the left.
        for edge, route in zip(data['edges'], geometry['edges']):
            sx, sy, sw, sh = geometry['cards'][edge['source']]
            tx, ty, tw, th = geometry['cards'][edge['target']]
            self.assertEqual(route['points'][0][0], sx + sw)
            self.assertEqual(route['points'][-1][0], tx)
            self.assertLess(sx, tx)
            self.assertTrue(sy <= route['points'][0][1] <= sy + sh and ty <= route['points'][-1][1] <= ty + th)

    def test_the_drawing_is_redone_from_the_data_without_the_instance(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        instance = write_canon(Path(temp.name) / 'instance', wide_canon())
        first, second = Path(temp.name) / 'first', Path(temp.name) / 'second'
        with contextlib.redirect_stdout(io.StringIO()) as shown:
            self.assertEqual(depmap.main([str(instance), '--out', str(first), '--layout', 'layered']), 0)
            self.assertEqual(depmap.main([str(first / 'dependency_map.json'), '--out', str(second), '--layout', 'layered']), 0)
        self.assertIn('9 units, 15 edges, 3 groups', shown.getvalue())
        for name in ('dependency_map.json', 'dependency_map.svg', 'dependency_map.html'):
            self.assertEqual((first / name).read_bytes(), (second / name).read_bytes(), name)
        with contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(depmap.main([str(first / 'dependency_map.json'), '--out', str(second), '--all']), 2)
            self.assertEqual(depmap.main([str(Path(temp.name) / 'nothing'), '--out', str(second)]), 2)
        self.assertIn('--all needs the instance', errors.getvalue())

    def test_without_elk_the_built_in_layout_is_used(self):
        data = self.map(wide_canon())
        with patch.object(draw.shutil, 'which', return_value=None):
            self.assertEqual(draw.render(data, 'auto')[2:], ('layered', None))
            with self.assertRaisesRegex(ValueError, 'the ELK layout needs Node on the PATH'):
                draw.render(data, 'elk')
        with patch.object(draw.shutil, 'which', return_value='node'), patch.dict(draw.os.environ, {'DO_MATH_ELKJS': ''}):
            missing = str(Path(tempfile.gettempdir()) / 'no-elkjs-here')
            engine, note = draw.render(data, 'auto', missing)[2:]
            self.assertEqual(engine, 'layered')
            self.assertIn('ELK was not used because it needs an elkjs package in ' + missing, note)

    def test_auto_takes_elk_only_when_the_groups_are_free_of_cycles(self):
        # In wide_canon the folder Lib holds the definition and the root, so it both feeds and uses the other folders.
        cyclic = self.map(wide_canon())
        one_way = self.map([definition('Lib.object', 'unit', module='Lib.Objects.Defs'),
                            statement('Lib.a', 'unit', mentions=['Lib.object'], module='Lib.Parts.A'),
                            statement('Lib.root', 'unit', uses=['Lib.a'], module='Lib.Main.Root')])
        self.assertTrue(draw.groups_in_a_cycle(cyclic))
        self.assertFalse(draw.groups_in_a_cycle(one_way))
        with patch.object(draw, 'find_elk', return_value=(Path('elkjs'), None)),                 patch.object(draw, 'elk', side_effect=RuntimeError('no layout')) as called:
            engine, note = draw.render(cyclic, 'auto')[2:]
            self.assertEqual(engine, 'layered')
            self.assertIn('the groups depend on each other in a cycle', note)
            called.assert_not_called()
            # Asked for by name, ELK is used whatever the groups are; a failure is then an error and not a fallback.
            with self.assertRaisesRegex(ValueError, 'the ELK layout failed: no layout'):
                draw.render(cyclic, 'elk')
            engine, note = draw.render(one_way, 'auto')[2:]
            self.assertEqual(engine, 'layered')
            self.assertIn('ELK failed (no layout)', note)
            self.assertEqual(called.call_count, 2)

    @unittest.skipUnless(draw.find_elk()[0], 'Node or the elkjs package is not present; the ELK layout is optional')
    def test_elk_lays_out_the_same_map_when_it_is_present(self):
        data = self.map(wide_canon())
        svg, _, engine, note = draw.render(data, 'elk')
        self.assertTrue(engine.startswith('ELK Layered'), engine)
        self.assertIsNone(note)
        tree = ElementTree.fromstring(svg)
        self.assertEqual(len(tree.findall(f".//{SVG}g[@class='node']")), len(data['units']))
        self.assertEqual(len(tree.findall(f".//{SVG}g[@class='edge']")), len(data['edges']))


class PublishedInstance(ScenarioCase):
    """The map of an instance whose canon was published through candidates, builds and review's verdicts."""

    def run_map(self, *options):
        out = self.root / ('map-' + '-'.join(option.strip('-') for option in options))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(depmap.main([str(self.instance), '--out', str(out), '--layout', 'layered', *options]), 0)
        for name in ('dependency_map.svg', 'dependency_map.html'):
            self.assertTrue((out / name).is_file())
        return read_json(out / 'dependency_map.json')

    def test_two_ways_of_proving_the_root(self):
        self.ways()
        data = self.run_map()
        units = {unit['id']: unit for unit in data['units']}
        # The steps stepE and stepF are folded, and strayS is a unit nothing uses.
        self.assertEqual(sorted(units), ['Small.colA', 'Small.diagD', 'Small.leafH', 'Small.monoB', 'Small.monoBAlt',
                                         'Small.oddSum', 'Small.root', 'Small.rootAlt', 'Small.unitG'])
        edges = {(edge['source'], edge['target']): edge for edge in data['edges']}
        proof_edges = {pair: (edge['kind'], edge['via']) for pair, edge in edges.items() if edge['kind'] != 'mention'}
        self.assertEqual(proof_edges, {
            ('Small.colA', 'Small.root'): ('direct', []),
            ('Small.monoB', 'Small.root'): ('contracted', ['Small.stepE']),
            ('Small.unitG', 'Small.root'): ('direct', []),
            ('Small.rootAlt', 'Small.root'): ('alternative', []),
            ('Small.colA', 'Small.rootAlt'): ('direct', []),
            ('Small.diagD', 'Small.rootAlt'): ('direct', []),
            ('Small.leafH', 'Small.colA'): ('direct', []),
            ('Small.monoBAlt', 'Small.monoB'): ('alternative', []),
            ('Small.leafH', 'Small.monoBAlt'): ('direct', [])})
        # The definition is joined to every statement that mentions it, and to no proof card.
        self.assertEqual(sorted(target for (source, target), edge in edges.items() if edge['kind'] == 'mention'),
                         ['Small.colA', 'Small.diagD', 'Small.leafH', 'Small.monoB', 'Small.root', 'Small.unitG'])
        self.assertEqual(edges[('Small.oddSum', 'Small.diagD')]['proof'], {'direct': False, 'via': ['Small.stepF']})
        self.assertEqual(sorted(data['folded']), ['Small.stepE', 'Small.stepF'])
        shown = {name.split('.')[1]: (unit['label'], unit.get('standing'), unit.get('settled'), unit.get('formal'))
                 for name, unit in units.items()}
        self.assertEqual(shown, {
            'oddSum': ('sum of odd numbers', None, None, None),
            'root': ('odd numbers sum to a square', 'accepted', False, False),
            'rootAlt': ('rootAlt', 'held', False, False),
            'colA': ('Col', 'held', False, False),
            'diagD': ('Diag', 'not_confirmed', False, False),
            'leafH': ('leafH', 'no_proof', False, False),
            'monoB': ('Mono', 'no_proof', False, False),
            'monoBAlt': ('monoBAlt', 'not_confirmed', False, False),
            'unitG': ('unitG', 'accepted', True, True)})
        self.assertEqual(units['Small.rootAlt']['proves'], 'Small.root')
        self.assertEqual(units['Small.colA']['statement'], 'The sum $1 + 3$ equals $4$.')
        self.assertEqual([group['id'] for group in data['groups']], ['Small'])
        self.assertEqual((data['root'], data['root_state'], data['scope']), ('Small.root', 'unresolved', 'root'))

        everything = self.run_map('--all')
        self.assertEqual(sorted(set(unit['id'] for unit in everything['units']) - set(units)), ['Small.strayS'])
        self.assertEqual(everything['scope'], 'all')


if __name__ == '__main__':
    unittest.main()
