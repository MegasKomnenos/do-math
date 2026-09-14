"""The declared reading sequence must reach the actual model input unchanged."""
import hashlib
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math.contracts import prompt_documents, render_prompt
from test_purpose_engine import PurposeHarness


class ReadingMapTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)
        source=Path(__file__).resolve().parents[2]
        shutil.copy2(source/'SKILL.md',self.root/'SKILL.md')
        shutil.copytree(source/'계약',self.root/'계약')
        (self.root/'GLOSSARY.md').write_text('The common definition is supplied here.',encoding='utf-8')
        (self.root/'references').mkdir()
        (self.root/'references/공통-실행.md').write_bytes(b'Common procedure.\r\nKeep this exact edition.\r\n')
        (self.root/'references/지식-저작과-재사용.md').write_text('Apply the existing result only within its actual assumptions.',encoding='utf-8')

    def test_declared_shared_procedures_are_supplied_in_reading_order(self):
        documents=prompt_documents('research_work',skill_root=self.root)
        self.assertEqual([d['path'] for d in documents],['SKILL.md','GLOSSARY.md','references/공통-실행.md',
                                                        'references/지식-저작과-재사용.md','계약/연구-수행.md'])
        for document in documents:
            raw=(self.root/document['path']).read_bytes()
            self.assertEqual(document['content'].encode('utf-8'),raw)
            self.assertEqual(document['sha256'],hashlib.sha256(raw).hexdigest())
        prompt=render_prompt('research_work',{'question':'Use the documented assumption'},skill_root=self.root)
        self.assertIn('Apply the existing result only within its actual assumptions.',prompt)
        self.assertNotIn('For research_plan:',prompt,'another role must not receive a separately maintained copy of planning rules')

    def test_changing_the_declared_role_path_changes_the_supplied_document(self):
        text=(self.root/'SKILL.md').read_text(encoding='utf-8')
        (self.root/'SKILL.md').write_text(text.replace('`계약/연구-수행.md`','`계약/특정-수행.md`'),encoding='utf-8')
        (self.root/'계약/특정-수행.md').write_text('The replacement is the declared role contract.',encoding='utf-8')
        documents=prompt_documents('research_work',skill_root=self.root)
        self.assertEqual(documents[-1]['path'],'계약/특정-수행.md')

    def test_missing_required_reference_is_not_silently_omitted(self):
        (self.root/'references/공통-실행.md').unlink()
        with self.assertRaises(FileNotFoundError): prompt_documents('research_work',skill_root=self.root)

    def test_missing_or_ambiguous_reading_map_is_an_error(self):
        original=(self.root/'SKILL.md').read_text(encoding='utf-8')
        for malformed in ('No reading map', original.replace('`SKILL.md`, `GLOSSARY.md`','`SKILL.md`, `SKILL.md`, `GLOSSARY.md`')):
            with self.subTest(text=malformed[:40]):
                (self.root/'SKILL.md').write_text(malformed,encoding='utf-8')
                with self.assertRaises(ValueError): prompt_documents('research_work',skill_root=self.root)


class DocumentContextTests(PurposeHarness):
    def test_declared_documents_have_recoverable_input_copies(self):
        engine,_=self.make()
        workspace=self.root/'preview';workspace.mkdir()
        context=engine._context({'role':'research_preparation'},workspace)
        self.assertIn('implementation_documents',context)
        documents=context['implementation_documents']
        self.assertEqual([d['path'] for d in documents], [d['path'] for d in engine._documents['research_preparation']])
        for row,original in zip(documents,engine._documents['research_preparation']):
            raw=(workspace/row['local_path']).read_bytes()
            self.assertEqual(raw,original['content'].encode('utf-8'))
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])

    def test_installed_reference_changes_are_part_of_the_version_check(self):
        engine,_=self.make()
        files=engine._installation_manifest()['files']
        self.assertIn('references/공통-실행.md',files)
        self.assertIn('references/지식-저작과-재사용.md',files)


if __name__=='__main__': unittest.main()
