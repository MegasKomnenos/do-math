"""정상 봉투의 한 좌표만 손상시켜 payload 수신기의 고유 거부 분기를 확인한다."""
from copy import deepcopy
import hashlib
import json
import re
import unittest

from do_math.canonical import canonical_json
from do_math.payloads import LIMIT, decode, encode, seal_large


class PayloadRejections(unittest.TestCase):
    def source(self):
        return encode({'contract_id': 'test', 'family': 'test',
                       'record': seal_large({'outer': ['A' * LIMIT]})})

    def test_reference_shape_and_coordinates_keep_valid_outer_envelope(self):
        mutations = (
            ('tokens', [True], 'invalid immutable payload reference'),
            ('tokens', [-1], 'invalid immutable payload reference'),
            ('tokens', ['outer', 3], 'invalid payload coordinate'),
            ('tokens', ['missing', 0], 'invalid payload coordinate'),
            ('tokens', ['outer', 'wrong'], 'invalid payload coordinate'),
            ('tokens', [], 'payload root overlaps'),
            ('bytes', LIMIT - 1, 'invalid immutable payload reference'),
            ('bytes', True, 'invalid immutable payload reference'),
            ('sha256', 'Z' * 64, 'invalid immutable payload reference'),
        )
        for field, value, reason in mutations:
            with self.subTest(field=field, value=value):
                envelope, blobs = self.source()
                self.assertEqual(decode(envelope, blobs.__getitem__), {'outer': ['A' * LIMIT]})
                envelope['payloads'][0][field] = value
                with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                    decode(envelope, blobs.__getitem__)

    def test_duplicate_reference_and_nonempty_coordinate_are_rejected(self):
        for duplicate in (False, True):
            envelope, blobs = self.source()
            if duplicate:
                envelope['payloads'].append(deepcopy(envelope['payloads'][0]))
            else:
                envelope['record']['outer'][0] = 'occupied'
            with self.assertRaisesRegex(ValueError, '^payload coordinate overlaps$'):
                decode(envelope, blobs.__getitem__)
        envelope, blobs = encode({'contract_id': 'test', 'family': 'test', 'record': seal_large('A' * LIMIT)})
        self.assertEqual(decode(envelope, blobs.__getitem__), 'A' * LIMIT)
        envelope['payloads'].append(deepcopy(envelope['payloads'][0]))
        with self.assertRaisesRegex(ValueError, '^payload root overlaps$'):
            decode(envelope, blobs.__getitem__)

    def test_blob_checks_distinguish_size_hash_canonical_and_leaf_shape(self):
        original = canonical_json('A' * LIMIT)
        cases = ((original[:-1], False, 'immutable payload bytes differ'),
                 (original.replace(b'A', b'B'), False, 'immutable payload bytes differ'),
                 (b' ' + original, True, 'noncanonical immutable payload'),
                 (canonical_json(['A' * LIMIT]), True, 'payload is not an externalized immutable field'))
        for raw, update_ref, reason in cases:
            with self.subTest(reason=reason, size=len(raw)):
                envelope, blobs = self.source()
                ref = envelope['payloads'][0]
                if update_ref:
                    ref['sha256'] = hashlib.sha256(raw).hexdigest()
                    ref['bytes'] = len(raw)
                    ref['path'] = 'runtime/artifacts/payload-' + ref['sha256'] + '/value.json'
                blobs[ref['path']] = raw
                with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                    decode(envelope, blobs.__getitem__)

    def test_inline_large_value_and_reference_order_fail_canonical_reencoding(self):
        envelope, blobs = self.source()
        envelope['payloads'] = {}
        with self.assertRaisesRegex(ValueError, '^payload references must be a list$'):
            decode(envelope, blobs.__getitem__)
        envelope = {'contract_id': 'test', 'family': 'test', 'record': 'A' * LIMIT}
        with self.assertRaisesRegex(ValueError, '^record differs from canonical payload encoding$'):
            decode(envelope, {}.__getitem__)
        envelope, blobs = encode({'contract_id': 'test', 'family': 'test',
                                  'record': seal_large({'a': 'A' * LIMIT, 'z': 'Z' * LIMIT})})
        envelope['payloads'].reverse()
        with self.assertRaisesRegex(ValueError, '^record differs from canonical payload encoding$'):
            decode(json.loads(canonical_json(envelope)), blobs.__getitem__)


if __name__ == '__main__':
    unittest.main()
