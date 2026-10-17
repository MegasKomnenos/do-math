"""Academic IDs and model extension values at their real receive/hash gates.

These families have no provider-native storage fixture. The tests use their
own producers and receivers; arbitrary values inside an allowed metadata
object remain distinct from an invalid value of the metadata field itself.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest

from do_math import academic, contracts, submission
from do_math.canonical import canonical_json
from do_math.payloads import json_safe
from do_math.values import compact_json_bytes, json_digest
from support.fakes.clock import FakeClock
from support.provider_native_inputs import EXTERNAL_JSON_VALUES
from support.record_builders import research_work_context, two_observation_output


class ExternalValueBoundaryTests(unittest.TestCase):
    def test_academic_id_gate_preserves_exact_text_and_rejects_other_axes(self):
        for label, value, _ in (*EXTERNAL_JSON_VALUES, ('bytes', b'raw', None)):
            source = [{'id': value, 'scope': 'S', 'assessor': 'research_plan', 'criteria': ['C']}]
            before = deepcopy(source)
            with self.subTest(label=label):
                if label == 'unicode':
                    result = academic.requirement_record(source)
                    expected = {'items': [{'id': value, 'scope': 'S', 'criteria': ['C'],
                        'assessor': 'research_plan', 'required_inputs': [], 'external_effects': []}]}
                    raw = (json.dumps(expected, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')
                    self.assertEqual(result, {**expected, 'sha256': hashlib.sha256(raw).hexdigest()})
                    self.assertEqual(canonical_json({'items': result['items']}), raw)
                    evidence = [{'criterion': 'C', 'satisfied': True, 'evidence': 'E'}]
                    assessed = academic.assess(value, {'goal_ref': 'G', 'records': []}, result, 'satisfied', evidence)
                    self.assertEqual(assessed['requirement_id'], value)
                    with self.assertRaisesRegex(ValueError, '^unknown requirement$'):
                        academic.assess(value.strip(), {}, result, 'satisfied', evidence)
                else:
                    detail = (repr(value) + " does not match '\\\\S'" if label == 'whitespace' else
                              repr(value) + " is not of type 'string'")
                    with self.assertRaisesRegex(ValueError, '^' + re.escape('academic requirement/id: ' + detail) + '$'):
                        academic.requirement_record(source)
                self.assertEqual(source, before)

    def test_academic_effect_default_and_explicit_null_use_the_same_receipt_consumer(self):
        for effect in ({'id': 'send', 'scope': 'S'}, {'id': 'send', 'scope': 'S', 'grant_id': None}):
            with self.subTest(effect=effect):
                requirements = academic.requirement_record([{'id': 'R', 'scope': 'S', 'criteria': ['C'],
                    'assessor': 'research_plan', 'external_effects': [effect]}])
                requirement = requirements['items'][0]
                self.assertEqual(requirement['external_effects'], [{'id': 'send', 'scope': 'S', 'grant_id': None}])
                self.assertIn(b'"grant_id": null', canonical_json(requirement))
                basis = {'goal_ref': 'G', 'records': []}
                operation = {'id': 'OP', 'status': 'confirmed', 'succeeded': True, 'grant_id': 'G',
                    'request_sha256': 'a' * 64, 'academic_binding': {'task_id': 'T', 'requirement_id': 'R',
                    'requirements_sha256': requirements['sha256'], 'solution_basis': basis, 'effect_id': 'send'}}
                self.assertEqual(academic.effect_receipts(requirement, task_id='T',
                    requirements_sha256=requirements['sha256'], solution_basis_value=basis,
                    runtime={'external_operations': {'OP': operation}}),
                    (True, [{'effect_id': 'send', 'operation_id': 'OP', 'grant_id': 'G', 'request_sha256': 'a' * 64}]))

    def test_extension_nested_axes_reach_real_checks_and_exact_hashes(self):
        for label, value, wire in EXTERNAL_JSON_VALUES:
            raw = b'{"knowledge_metadata":[{"title":"A","uncertainty_assessment":{"value":' + wire + b'}}]}'
            with self.subTest(label=label):
                if label == 'decimal' or label.startswith('unsafe-'):
                    reason = ('JSON floating-point numbers are not permitted' if label == 'decimal' else
                              'JSON integers must be safe integers')
                    with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                        submission.load_extensions(raw)
                    continue
                extensions = submission.load_extensions(raw)
                self.assertEqual(extensions, {'knowledge_metadata': [{'title': 'A', 'uncertainty_assessment': {'value': value}}]})
                before = deepcopy(extensions)
                output, context = two_observation_output(), research_work_context()
                output['integration_bundles'][0]['members'].append('activity-extensions.json/knowledge_metadata/0')
                schema = contracts.action_schema(context['action'])
                with tempfile.TemporaryDirectory() as directory:
                    checked = submission.check_submission(output, schema, context, extensions, Path(directory),
                        mode='receiver', execution_id='EX-values', tool_sha256='a' * 64, clock=FakeClock())
                self.assertEqual(checked['issues'], [])
                self.assertTrue(checked['passed'])
                expected = (json.dumps(before, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')
                self.assertEqual(canonical_json(extensions), expected)
                self.assertEqual(checked['input_hashes']['extensions'], hashlib.sha256(expected).hexdigest())
                self.assertEqual(extensions, before)
                self.assertIn(b'"execution_id": "EX-values"', canonical_json(checked))

    def test_extension_absence_null_and_empty_families_stay_distinct(self):
        cases = ((b'{}', {}, []), (b'{"research_insights":[]}', {}, []),
                 (b'null', None, [('activity-extensions.json', "None is not of type 'object'")]),
                 (b'[]', [], [('activity-extensions.json', "[] is not of type 'object'")]),
                 (b'{"research_insights":null}', {'research_insights': None},
                  [('activity-extensions.json/research_insights', "None is not of type 'array'"),
                   ('output/integration_bundles', 'extension families must be arrays: research_insights')]),
                 (b'{"research_insights":{}}', {'research_insights': {}},
                  [('activity-extensions.json/research_insights', "{} is not of type 'array'"),
                   ('output/integration_bundles', 'extension families must be arrays: research_insights')]))
        output = {'summary': 'S', 'used_sources': [], 'questions': [], 'report': 'R', 'remaining_work': []}
        context = {'action': {'role': 'maintenance'}, 'execution_id': 'EX-null', 'snapshot': 'fixed'}
        schema = contracts.action_schema(context['action'])
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            self.assertEqual(submission.read_extensions(workspace), {})
            for raw, expected, issues in cases:
                with self.subTest(raw=raw):
                    (workspace / 'activity-extensions.json').write_bytes(raw)
                    value = submission.read_extensions(workspace)
                    self.assertEqual(value, expected)
                    self.assertEqual((workspace / 'activity-extensions.json').read_bytes(), raw)
                    checked = submission.check_submission(output, schema, context, value, Path(directory),
                        mode='receiver', execution_id='EX-null', tool_sha256='a' * 64, clock=FakeClock())
                    self.assertEqual([(row['path'], row['message']) for row in checked['issues']], issues)
                    self.assertEqual(checked['passed'], not issues)
                    encoded = (json.dumps(expected, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')
                    self.assertEqual(checked['input_hashes']['extensions'], hashlib.sha256(encoded).hexdigest())
                    self.assertEqual(value, expected)
        raw = b'\xff\x00'
        with self.assertRaises(UnicodeDecodeError) as rejected:
            submission.load_extensions(raw)
        self.assertEqual((rejected.exception.object, rejected.exception.encoding,
                          rejected.exception.start, rejected.exception.end, rejected.exception.reason),
                         (raw, 'utf-8', 0, 1, 'invalid start byte'))

    def test_wire_codec_and_byte_projection_have_independent_exact_expectations(self):
        for label, value, wire in EXTERNAL_JSON_VALUES:
            with self.subTest(label=label):
                self.assertEqual(compact_json_bytes(value), wire)
                self.assertEqual(json_digest(value), hashlib.sha256(wire).hexdigest())
        with self.assertRaisesRegex(TypeError, '^Object of type bytes is not JSON serializable$'):
            compact_json_bytes(b'\xff\x00')
        raw = b'\xff\x00'
        self.assertEqual(json_safe(raw), {'sha256': hashlib.sha256(raw).hexdigest(), 'text': '\ufffd\x00', 'base64': '/wA='})
