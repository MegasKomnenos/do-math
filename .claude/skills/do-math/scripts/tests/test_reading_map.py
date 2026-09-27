"""The declared reading sequence must reach the actual model input unchanged."""
import hashlib
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math.contracts import prompt_documents, render_prompt
from purpose_fixtures import ActivatedPurposeHarness


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
        (self.root/'references/모델과-실행예산.md').write_text('Select a model from difficulty and importance, then wait for its slot.',encoding='utf-8')
        (self.root/'references/지식-저작과-재사용.md').write_text('Apply the existing result only within its actual assumptions.',encoding='utf-8')
        (self.root/'references/학술자료-활용.md').write_text('Read the original rendered equation before criticizing its transcription.',encoding='utf-8')
        (self.root/'references/자기-점검.md').write_text('Answer each due self-check rule with its evidence.',encoding='utf-8')

    def test_declared_shared_procedures_are_supplied_in_reading_order(self):
        documents=prompt_documents('research_work',skill_root=self.root)
        self.assertEqual([d['path'] for d in documents],['SKILL.md','GLOSSARY.md','references/공통-실행.md','references/지식-저작과-재사용.md',
                                                        'references/학술자료-활용.md','references/자기-점검.md','계약/연구-수행.md'])
        for document in documents:
            raw=(self.root/document['path']).read_bytes()
            self.assertEqual(document['content'].encode('utf-8'),raw)
            self.assertEqual(document['sha256'],hashlib.sha256(raw).hexdigest())
        prompt=render_prompt('research_work',{'question':'Use the documented assumption'},skill_root=self.root)
        self.assertIn('Apply the existing result only within its actual assumptions.',prompt)
        self.assertNotIn('For research_plan:',prompt,'another role must not receive a separately maintained copy of planning rules')
        self.assertNotIn('Select a model from difficulty and importance',prompt,'model selection rules go only to the roles that assess models')

    def test_role_rows_add_their_references_after_the_common_documents(self):
        common=['SKILL.md','GLOSSARY.md','references/공통-실행.md','references/지식-저작과-재사용.md','references/학술자료-활용.md']
        expected={'research_preparation':['references/모델과-실행예산.md','references/과제-착수조건.md','계약/후보-준비.md'],
                  'research_plan':['references/모델과-실행예산.md','계약/연구-계획.md'],
                  'task_contract_review':['references/모델과-실행예산.md','references/과제-착수조건.md','계약/작업-계약-검토.md'],
                  'operational_review':['references/자기-점검.md','계약/운영-점검.md'],
                  'intent_interpretation':['references/입력-소비자.md','계약/의도-해석.md'],
                  'goal_audit':['계약/목표-감사.md']}
        for name in ('references/과제-착수조건.md','references/입력-소비자.md'):
            (self.root/name).write_text('Role reference.',encoding='utf-8')
        for role,paths in expected.items():
            with self.subTest(role=role):
                self.assertEqual([d['path'] for d in prompt_documents(role,skill_root=self.root)],common+paths)

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


class DocumentContextTests(ActivatedPurposeHarness):
    def test_declared_documents_have_recoverable_input_copies(self):
        engine,_=self.make_active()
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
        engine,_=self.make_active()
        files=engine._installation_manifest()['files']
        self.assertIn('references/공통-실행.md',files)
        self.assertIn('references/지식-저작과-재사용.md',files)
        self.assertIn('references/학술자료-활용.md',files)


if __name__=='__main__': unittest.main()
