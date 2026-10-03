"""첫 full T3의 canonical/values/parser 빈 분기를 입력·결과로 고정한다."""
from copy import deepcopy
import hashlib
import re
import unittest

from do_math.canonical import FrozenText, canonical_json, exact_content_hash, validate_storage_value
from do_math.payloads import json_safe, seal
from do_math.ports.git_backend import GitBackendError
from do_math.storage_finish_git_output import parse_object_info
from do_math.values import distinct_texts, parse_utc


class Text(str):
    """JSON 문자열 하위형 경로의 입력."""


class Mapping(dict):
    """일반 dict의 빠른 경로 밖 입력."""


class Sequence(list):
    """일반 list의 빠른 경로 밖 입력."""


class ValueBranches(unittest.TestCase):
    def test_distinct_texts_refuses_nonlists_and_blank_or_nonstrings_before_hashing(self):
        for value in (None, False, 0, 'text', {}, [[]], [{}], [''], [' \t\n']):
            with self.subTest(value=value), self.assertRaisesRegex(
                    ValueError, '^references requires distinct nonempty strings$'):
                distinct_texts(value, 'references')

    def test_distinct_texts_preserves_exact_text_in_an_independent_list(self):
        original = ['원문', ' e\N{COMBINING ACUTE ACCENT} ']
        result = distinct_texts(original, 'references', nonempty=True)
        self.assertEqual(result, ['원문', ' e\N{COMBINING ACUTE ACCENT} '])
        self.assertIsNot(result, original)
        result.append('new')
        self.assertEqual(original, ['원문', ' e\N{COMBINING ACUTE ACCENT} '])
        empty = []
        self.assertEqual(distinct_texts(empty, 'references'), [])
        self.assertIsNot(distinct_texts(empty, 'references'), empty)

    def test_subclass_values_and_sealed_values_keep_exact_encoding(self):
        value = Mapping({Text('key'): Sequence([Text('한글'), None, True, 3])})
        expected = b'{\n  "key": [\n    "' + '한글'.encode() + b'",\n    null,\n    true,\n    3\n  ]\n}\n'
        self.assertEqual(canonical_json(value), expected)
        self.assertEqual(exact_content_hash(value), hashlib.sha256(expected).hexdigest())
        self.assertIsNone(validate_storage_value({Text('key'): 'value'}))
        text = seal('원문')
        self.assertIsInstance(text, FrozenText)
        self.assertIs(deepcopy(text), text)
        self.assertEqual(canonical_json(text), '"원문"\n'.encode())
        self.assertIsNone(validate_storage_value(text))

    def test_subclass_surrogate_keys_nonstring_keys_and_nonjson_are_refused(self):
        cases = ((Text(chr(0xD800)), 'JSON strings cannot contain surrogate code points'),
                 (Mapping({3: 'value'}), 'JSON object keys must be strings'),
                 (Mapping({Text(chr(0xD800)): 'value'}), 'JSON strings cannot contain surrogate code points'),
                 ({Text(chr(0xD800)): None}, 'JSON strings cannot contain surrogate code points'),
                 ((1, 2), 'value is not JSON-serializable'))
        for value, reason in cases:
            with self.subTest(value=repr(value)), self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                canonical_json(value)

    def test_time_requires_offset_and_float_projection_is_explicit(self):
        with self.assertRaisesRegex(ValueError, '^timestamp requires a timezone: 2026-01-01T00:00:00$'):
            parse_utc('2026-01-01T00:00:00')
        self.assertEqual(parse_utc('2026-01-01T09:00:00+09:00').isoformat(), '2026-01-01T00:00:00+00:00')
        self.assertEqual(json_safe({'x': [1.25, True, 2**53]}),
                         {'x': [{'reported_decimal': '1.25'}, True, str(2**53)]})

    def test_git_info_refuses_count_and_malformed_rows(self):
        for raw, reason in ((b'', 'batch object check response count differs'),
                            (b'a blob nope\n', 'invalid batch object check row for ref'),
                            (b'a blob\n', 'invalid batch object check row for ref')):
            with self.subTest(raw=raw), self.assertRaisesRegex(GitBackendError, '^' + reason + '$'):
                parse_object_info(['ref'], raw)
        self.assertEqual(parse_object_info(['ref', 'missing'], b'a blob 3\nmissing missing\n'),
                         [('a', 'blob', 3), None])

    def test_profile_reference_accepts_generated_profiles_and_pins_each_malformed_shape(self):
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.execution_profiles import build_profiles, profile_ref
        from do_math.values import validate_profile_ref
        from support.entry import entry

        profiles = build_profiles(DEFAULT_CONFIG, host=entry().ports.host)['execution_profiles']
        self.assertTrue(profiles, 'no actual profile producer output was checked')
        for profile in profiles.values():
            with self.subTest(profile=profile['id']):
                reference = profile_ref(profile)
                before = deepcopy(reference)
                self.assertIsNone(validate_profile_ref(reference))
                self.assertEqual(reference, before)
                invalid = [('not an object', value) for value in (None, [], 'reference', 1)]
                invalid.extend(('missing ' + key, {name: value for name, value in reference.items() if name != key})
                               for key in reference)
                invalid.append(('extra field', {**reference, 'unexpected': True}))
                for field, values in (
                        ('id', (None, 1, '', ' \t\n')),
                        ('revision', (None, '1', 1.0, True, False, 0, -1)),
                        ('sha256', (None, 1, '', 'a' * 63, 'a' * 65, 'g' * 64, 'A' * 64))):
                    invalid.extend((field + '=' + repr(value), {**reference, field: value}) for value in values)
                for label, value in invalid:
                    with self.subTest(shape=label), self.assertRaisesRegex(
                            ValueError, '^profile reference requires exact id, revision and sha256$'):
                        validate_profile_ref(value)


if __name__ == '__main__':
    unittest.main()
