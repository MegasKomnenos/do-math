"""Guard the glossary boundary without claiming to decide mathematical equality."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from glossary import check_glossary, check_local_glossary, FIELDS, LOCAL_FIELDS, LOCAL_MARKER
from check import check_session

def snapshot():
    return '\n'.join(['<!-- do-math-glossary -->',
        '[History](glossary-history.md)', '<a id="term-1"></a>', '## 1. Term',
        '| Field | Content |', '|---|---|']+[f'| {field} | Value |' for field in FIELDS])+'\n'

class GlossaryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.out=self.root/'session/output'
        self.out.mkdir(parents=True)
        self.write(snapshot())
        for f in ('glossary-history.md','research-status.md'):
            (self.out/f).write_text('Evidence',encoding='utf-8')

    def write(self, s):
        (self.out/'glossary.md').write_text(s,encoding='utf-8')

    def test_valid_with_expression_pipes_and_current_scope(self):
        self.write(snapshot().replace('| Definition | Value |','| Definition | A={x: |x|<1}; q≥2. |'))
        self.assertEqual(check_glossary(self.out),[])

    def test_missing_files_and_format(self):
        (self.out/'glossary-history.md').unlink()
        self.assertTrue(check_glossary(self.out))
        (self.out/'glossary-history.md').write_text('History',encoding='utf-8')
        self.write(snapshot().replace('<!-- do-math-glossary -->',''))
        self.assertTrue(check_glossary(self.out))

    def test_duplicate_status_and_appended_history_rejected(self):
        for tail in ['| Additional Lean correspondence | A later accepted result |\n',
                     '| Current formal correspondence | Another status |\n',
                     'Current formal acceptance supplement: later state.\n']:
            self.write(snapshot()+tail)
            self.assertTrue(check_glossary(self.out),tail)

    def test_empty_field_duplicate_id_and_missing_anchor_rejected(self):
        for s in [snapshot().replace('| Provenance | Value |','| Provenance |  |'),
                  snapshot()+snapshot()[snapshot().index('<a id='):],
                  snapshot().replace('<a id="term-1"></a>','')]:
            self.write(s);self.assertTrue(check_glossary(self.out))

    def test_relation_links(self):
        self.write(snapshot().replace('| Related expressions | Value |','| Related expressions | [self](#term-1) |'))
        self.assertEqual(check_glossary(self.out),[])
        self.write(snapshot().replace('| Related expressions | Value |','| Related expressions | [missing](#term-2) |'))
        self.assertTrue(check_glossary(self.out))
        self.write(snapshot().replace('| Related expressions | Value |','| Related expressions | [family](glossary-relations.md) |'))
        self.assertTrue(check_glossary(self.out))
        (self.out/'glossary-relations.md').write_text('Family',encoding='utf-8')
        self.assertEqual(check_glossary(self.out),[])
        (self.out/'glossary-relations.md').write_text('[missing](glossary.md#term-2)',encoding='utf-8')
        self.assertTrue(check_glossary(self.out))

    def test_swapped_anchors_do_not_point_to_wrong_definitions(self):
        first=snapshot().replace('term-1','term-2')
        second=snapshot()[snapshot().index('<a id='):].replace('## 1.','## 2.')
        self.write(first+second)
        self.assertTrue(check_glossary(self.out))

    def fixture(self):
        context=self.root/'context.md';context.write_text('Context',encoding='utf-8')
        (self.root/'knowledge').mkdir(exist_ok=True)
        inp=dict(instance=str(self.root),category='plan',
                 context={'common':[str(context)],'category':str(context)},
                 task={'instructions':'Plan','references':[],'events':[],'previous_plan':None})
        data=dict(category='plan',overview={'title':'Plan','summary':'Fixture'},references=[],
                  supersedes=[],reason='Fixture',research=[],explorations=[],reviews=[],goal_review=None,wait=None)
        (self.out.parent/'input.json').write_text(json.dumps(inp),encoding='utf-8')
        (self.out/'output.json').write_text(json.dumps(data),encoding='utf-8')
        return check_session(self.out.parent)

    def test_every_submitted_plan_requires_current_snapshot(self):
        self.assertEqual(self.fixture(),[])
        self.write('An old glossary format')
        self.assertTrue(self.fixture())

    def test_aliases_belong_in_archive_not_current_entries(self):
        self.write(snapshot()+'| Per-record aliases | Historical name |\n')
        self.assertTrue(check_glossary(self.out))


def local(entries=1, candidate='None'):
    lines = [LOCAL_MARKER, 'Local glossary of this record. Global glossary applied: k1 (glossary.md).']
    for n in range(1, entries + 1):
        lines += [f'<a id="local-{n}"></a>', f'## {n}. Term {n}', '| Field | Content |', '|---|---|']
        lines += [f'| {field} | {candidate if field == "Global candidate" else "Value"} |' for field in LOCAL_FIELDS]
    return '\n'.join(lines) + '\n'


class LocalGlossaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name)

    def write(self, s):
        (self.out / 'glossary-local.md').write_text(s, encoding='utf-8')

    def test_entries_zero_entries_and_candidates_are_valid(self):
        for source in (local(2), local(0), local(1, 'Needed by the formalization task posted next.')):
            self.write(source)
            self.assertEqual(check_local_glossary(self.out), [], source)

    def test_missing_empty_or_unmarked_file_rejected(self):
        self.assertTrue(check_local_glossary(self.out))
        self.write('  \n')
        self.assertTrue(check_local_glossary(self.out))
        self.write(local(1).replace(LOCAL_MARKER, ''))
        self.assertTrue(check_local_glossary(self.out))
        self.write(local(1).replace(LOCAL_MARKER, '<!-- do-math-glossary -->'))
        self.assertTrue(check_local_glossary(self.out))

    def test_fields_once_in_order_including_candidate(self):
        for source in (local(1).replace('| Global candidate | None |\n', ''),
                       local(1).replace('| Kind | Value |\n', ''),
                       local(1) + '| Global candidate | Again |\n',
                       local(1).replace('| Global candidate | None |', '| Global candidate |  |'),
                       local(1) + 'Later note outside the fields.\n'):
            self.write(source)
            self.assertTrue(check_local_glossary(self.out), source)

    def test_anchors_and_links_use_local_prefix(self):
        self.write(local(1).replace('local-1', 'term-1'))
        self.assertTrue(check_local_glossary(self.out))
        self.write(local(2).replace('<a id="local-2"></a>\n', ''))
        self.assertTrue(check_local_glossary(self.out))
        self.write(local(2).replace('| Related expressions | Value |', '| Related expressions | [first](#local-1) |', 1))
        self.assertEqual(check_local_glossary(self.out), [])
        self.write(local(1).replace('| Related expressions | Value |', '| Related expressions | [missing](#local-2) |'))
        self.assertTrue(check_local_glossary(self.out))

if __name__=='__main__':
    unittest.main()
