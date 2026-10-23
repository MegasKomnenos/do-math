"""Guard the glossary boundary without claiming to decide mathematical equality."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from glossary import check_glossary, FIELDS
from check import check_session

def snapshot():
    return '\n'.join(['<!-- do-math-glossary -->',
        '[History](glossary-history.md)', '<a id="term-1"></a>', '## 1. Term',
        '| 칸 | 내용 |', '|---|---|']+[f'| {field} | Value |' for field in FIELDS])+'\n'

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
        self.write(snapshot().replace('| 정의 | Value |','| 정의 | A={x: |x|<1}; q≥2. |'))
        self.assertEqual(check_glossary(self.out),[])

    def test_missing_files_and_format(self):
        (self.out/'glossary-history.md').unlink()
        self.assertTrue(check_glossary(self.out))
        (self.out/'glossary-history.md').write_text('History',encoding='utf-8')
        self.write(snapshot().replace('<!-- do-math-glossary -->',''))
        self.assertTrue(check_glossary(self.out))

    def test_duplicate_status_and_appended_history_rejected(self):
        for tail in ['| Lean 추가 대응 | A later accepted result |\n',
                     '| 현재 형식 대응 | Another status |\n',
                     '현재 형식 수용 보완: later state.\n']:
            self.write(snapshot()+tail)
            self.assertTrue(check_glossary(self.out),tail)

    def test_empty_field_duplicate_id_and_missing_anchor_rejected(self):
        for s in [snapshot().replace('| 출처 | Value |','| 출처 |  |'),
                  snapshot()+snapshot()[snapshot().index('<a id='):],
                  snapshot().replace('<a id="term-1"></a>','')]:
            self.write(s);self.assertTrue(check_glossary(self.out))

    def test_relation_links(self):
        self.write(snapshot().replace('| 관련 표현 | Value |','| 관련 표현 | [self](#term-1) |'))
        self.assertEqual(check_glossary(self.out),[])
        self.write(snapshot().replace('| 관련 표현 | Value |','| 관련 표현 | [missing](#term-2) |'))
        self.assertTrue(check_glossary(self.out))
        self.write(snapshot().replace('| 관련 표현 | Value |','| 관련 표현 | [family](glossary-relations.md) |'))
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
        self.write(snapshot()+'| 기록별 이명 | Historical name |\n')
        self.assertTrue(check_glossary(self.out))

if __name__=='__main__':
    unittest.main()
