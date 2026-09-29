"""Preflight (layer 2): read-only structural checks of an installed skill copy."""
import hashlib
from pathlib import Path
import shutil
import tempfile
import unittest

from do_math.contracts import reading_map
from do_math.preflight import INSTALLED_DOCUMENTS, inspect_bundle

SKILL = Path(__file__).resolve().parents[3]


class PreflightTests(unittest.TestCase):
    """A copy of the documents the role reading map and the preflight name, beside the product's own code."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / 'skill'
        names = {name for assigned in reading_map(skill_root=SKILL).values() for name in assigned}
        names.update(INSTALLED_DOCUMENTS)
        for name in names:
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SKILL / name, destination)

    def documents(self, report):
        check, = [row for row in report['checks'] if row['check'] == 'installed_documents']
        return check

    def test_current_installation_has_all_roles_and_schemas(self):
        """About 0.2-0.8 s, over the 0.2 s unit budget: preflight hashes every installed document and checks every role schema (the first test of the process fills the schema cache)."""
        report = inspect_bundle(self.root)
        self.assertEqual(report['status'], 'verified')
        self.assertEqual(report['scope'], 'installed_skill_structure')
        self.assertEqual([row['check'] for row in report['checks']], ['installed_documents', 'role_output_schemas'])
        self.assertEqual([row['roles'] for row in report['checks']], [10, 10])
        self.assertEqual([row['status'] for row in report['checks']], ['verified', 'verified'])
        self.assertIn('document_semantics', report['not_verified'])
        self.assertTrue(set(INSTALLED_DOCUMENTS) <= set(self.documents(report)['documents']))
        schemas = report['checks'][1]['schemas']
        self.assertIn('recovery', schemas)
        self.assertTrue(all(len(digest) == 64 for digest in schemas.values()))

    def assert_incomplete(self, phrase):
        report = inspect_bundle(self.root)
        self.assertEqual(report['status'], 'incomplete')
        documents = self.documents(report)
        self.assertEqual(documents['status'], 'incomplete')
        self.assertIn(phrase, documents['reason'])
        self.assertNotIn('documents', documents)

    def test_missing_required_document_is_incomplete(self):
        (self.root / 'GLOSSARY.md').unlink()
        self.assert_incomplete('GLOSSARY.md')

    def test_reading_map_cannot_escape_skill(self):
        path = self.root / 'SKILL.md'
        path.write_text(path.read_text(encoding='utf-8').replace('`GLOSSARY.md`', '`../outside.md`'), encoding='utf-8')
        self.assert_incomplete('reading documents must be Markdown files within the skill')

    def test_missing_operating_contract_is_incomplete(self):
        """About 0.2-0.8 s, over the 0.2 s unit budget: preflight hashes every installed document and checks every role schema (the first test of the process fills the schema cache)."""
        (self.root / 'references/CLI-실행-계약.md').unlink()
        self.assert_incomplete('CLI-실행-계약.md')

    def test_missing_independent_operator_contract_is_incomplete(self):
        (self.root / '계약/독립-운영.md').unlink()
        self.assert_incomplete('독립-운영.md')

    def test_missing_scheduler_entrypoint_is_incomplete(self):
        """About 0.2-0.8 s, over the 0.2 s unit budget: preflight hashes every installed document and checks every role schema (the first test of the process fills the schema cache)."""
        (self.root / 'scripts/operator_schedule.ps1').unlink()
        self.assert_incomplete('operator_schedule.ps1')

    def test_an_installed_document_behind_a_junction_out_of_the_skill_is_incomplete(self):
        """About 0.2-0.8 s, over the 0.2 s unit budget: preflight hashes every installed document and checks every role schema (the first test of the process fills the schema cache)."""
        import _winapi
        outside = self.root.parent / 'outside-scripts'
        (self.root / 'scripts').rename(outside)
        _winapi.CreateJunction(str(outside), str(self.root / 'scripts'))
        self.assert_incomplete('document leaves the skill: scripts/')

    def test_an_empty_installed_document_is_incomplete(self):
        """About 0.2-0.8 s, over the 0.2 s unit budget: preflight hashes every installed document and checks every role schema (the first test of the process fills the schema cache)."""
        (self.root / 'requirements.txt').write_text(' \n', encoding='utf-8')
        self.assert_incomplete('empty document: requirements.txt')

    def test_a_schema_must_be_well_formed_for_both_validator_drafts(self):
        from jsonschema.exceptions import SchemaError
        from do_math.preflight import _check_schema_pair
        self.assertIsNone(_check_schema_pair('{"type": "object", "x-contract-id": "c", "$schema": "s"}'))
        with self.assertRaisesRegex(SchemaError, "'objekt' is not valid under any of the given schemas"):
            _check_schema_pair('{"type": "objekt"}')

    def test_read_only_and_observed_document_hashes(self):
        """About 0.2-0.8 s, over the 0.2 s unit budget: preflight hashes every installed document and checks every role schema (the first test of the process fills the schema cache)."""
        def hashes():
            return {p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in self.root.rglob('*') if p.is_file()}
        before = hashes()
        report = inspect_bundle(self.root)
        self.assertEqual(before, hashes())
        documents = report['checks'][0]['documents']
        self.assertTrue(documents)
        for name, digest in documents.items():
            self.assertEqual(digest, before[name])


if __name__ == '__main__':
    unittest.main()
