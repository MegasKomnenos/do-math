"""공개 원천 바이트와 요청 식별자의 정확한 거부 경계."""
from copy import deepcopy
import unittest

from do_math.control_contracts import (control_request_id, normalized_source,
    normalized_source_bytes, validate_request_id)


class SourceGuardTests(unittest.TestCase):
    def test_source_decoder_requires_the_producers_exact_outer_shape(self):
        original = normalized_source('원문.txt', b'exact source bytes')
        cases = [None, False, 0, 'source', []]
        cases.extend({key: value for key, value in original.items() if key != omitted}
                     for omitted in original)
        cases.append({**original, 'extra': True})
        for malformed in cases:
            with self.subTest(malformed=malformed):
                before = deepcopy(malformed)
                with self.assertRaisesRegex(ValueError, '^normalized source requires exact name, body, hash and size$'):
                    normalized_source_bytes(malformed)
                self.assertEqual(malformed, before)
        self.assertEqual(normalized_source_bytes(original), b'exact source bytes')

    def test_invalid_request_identifiers_and_idempotency_keys_are_rejected(self):
        for value in (None, 0, '', 'a/b', '한글', 'a' * 129):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, '^request_id must be a safe nonempty ASCII identifier$'):
                    validate_request_id(value)
        for value in (False, [], ''):
            with self.subTest(key=value):
                with self.assertRaisesRegex(ValueError, '^idempotency_key must be a nonempty string$'):
                    control_request_id('RI-one', 'pause', idempotency_key=value)

    def test_source_decoder_rejects_only_the_corrupted_inner_field(self):
        original = normalized_source('원문.txt', '제약\r\ne\N{COMBINING ACUTE ACCENT}\n'.encode('utf-8'))
        cases = [('name', '../x', 'source name must be a file name'),
                 ('body_base64', '%%%!', 'source body is not strict base64'),
                 ('body_base64', None, 'source body is not strict base64'),
                 ('sha256', '0' * 64, 'source bytes differ from their declared hash or size'),
                 ('bytes', original['bytes'] + 1, 'source bytes differ from their declared hash or size')]
        for field, value, reason in cases:
            with self.subTest(field=field, value=value):
                damaged = {**original, field: value}
                before = deepcopy(damaged)
                with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                    normalized_source_bytes(damaged)
                self.assertEqual(damaged, before)
        self.assertEqual(normalized_source_bytes(original), '제약\r\ne\N{COMBINING ACUTE ACCENT}\n'.encode('utf-8'))
