"""첫 full T3의 contracts 미도달 반려를 정확한 계약 사유로 고정한다."""
from copy import deepcopy
from pathlib import Path
import re
import tempfile
import unittest

from do_math import contracts
from support.role_answers import candidate, review_items


class ContractRejectionTests(unittest.TestCase):
    def test_revision_requires_an_existing_positive_integer_edition(self):
        wire = candidate(revises='TK-existing')
        wire['profile_refs'] = [{'id': 'EP-work', 'revision': 1, 'sha256': 'a' * 64}]
        with self.assertRaisesRegex(ValueError, '^revised task candidate requires its existing contract$'):
            contracts.task_candidate_record(wire, task_id='TK-existing')
        for revision in (None, False, 0, -1, 1.5, '1'):
            with self.subTest(revision=revision), self.assertRaisesRegex(ValueError, '^existing task revision is invalid$'):
                contracts.task_candidate_record(wire, task_id='TK-existing',
                                               previous={'id': 'TK-existing', 'revision': revision})

    def test_unknown_roles_and_nonobject_context_have_distinct_errors(self):
        for function in (contracts.schema_for, contracts.prompt_documents):
            with self.subTest(function=function.__name__), self.assertRaisesRegex(ValueError, '^unknown do-math role: absent$'):
                function('absent')
        with self.assertRaisesRegex(TypeError, '^context must be an object$'):
            contracts.render_prompt('maintenance', [], documents=[])

    def test_review_approval_requires_evidence_and_unresolved_requires_missing_inputs(self):
        for evidence, missing, decision, reason in [
                ([], [], 'approved', 'approval needs evidence and no missing inputs'),
                (['TK-1'], ['source.txt'], 'approved', 'approval needs evidence and no missing inputs'),
                (['TK-1'], [], 'unresolved', 'unresolved contract inspection needs missing inputs')]:
            output = review_items(['TK-1'])
            output['item_reviews'][0].update(evidence_refs=evidence, missing_inputs=missing, decision=decision)
            with self.subTest(decision=decision, missing=missing), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                contracts.contract_review_decision(output)

    def test_reading_map_rejects_unknown_duplicate_empty_and_unsafe_rows(self):
        baseline = ['| common | `SKILL.md` `GLOSSARY.md` |',
                    *['| ' + role + ' | `' + role + '.md` |' for role in contracts.ROLES]]
        variants = [
            (baseline + ['| absent | `absent.md` |'], 'reading map contains an unknown role'),
            (baseline + [baseline[-1]], 'reading map requires distinct roles and document paths'),
            ([*baseline[:-1], '| maintenance | |'], 'reading map requires distinct roles and document paths'),
            ([*baseline[:-1], '| maintenance | `a.md` `a.md` |'], 'reading map requires distinct roles and document paths'),
            ([*baseline[:-1], '| maintenance | `../outside.md` |'], 'reading documents must be Markdown files within the skill'),
            ([*baseline[:-1], '| maintenance | `a.txt` |'], 'reading documents must be Markdown files within the skill'),
            (baseline[:-1], 'reading map must assign the common definitions and every role'),
            ([*baseline[:-1], '| maintenance | `GLOSSARY.md` |'], 'a role must receive each document exactly once'),
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for rows, reason in variants:
                with self.subTest(reason=reason, rows=rows[-1]):
                    (root / 'SKILL.md').write_text('<!-- role-reading-map:start -->\n' + '\n'.join(rows)
                                                 + '\n<!-- role-reading-map:end -->', encoding='utf-8')
                    with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                        contracts.reading_map(skill_root=root)

    def test_schema_copies_do_not_share_nested_fields_between_roles_or_calls(self):
        for role in contracts.ROLES:
            with self.subTest(role=role):
                original = contracts.action_schema({'role': role})
                changed = contracts.action_schema({'role': role})
                changed['properties']['summary']['description'] = '독립 사본'
                self.assertEqual(contracts.action_schema({'role': role}), original)
                self.assertNotEqual(changed, original)
