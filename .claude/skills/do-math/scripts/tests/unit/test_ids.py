"""ULID composition is a pure function of prefix, milliseconds, and ten entropy bytes."""
import re
import unittest

from do_math.ids import ULID_PATTERN, ulid


class UlidTests(unittest.TestCase):
    def test_encoding_matches_the_identifier_the_product_has_always_produced(self):
        # Captured from repository.new_id with time_ns=1_700_000_000_123_456_789
        # and entropy bytes 0..9 before the composition moved into do_math.ids.
        self.assertEqual(ulid('EX', 1_700_000_000_123, bytes(range(10))), 'EX-01HF7YAT3V000G40R40M30E209')

    def test_later_milliseconds_sort_after_earlier_ones(self):
        entropy = b'\xff' * 10
        self.assertLess(ulid('EX', 1, entropy), ulid('EX', 2, b'\x00' * 10))

    def test_identifier_has_the_stored_shape(self):
        self.assertRegex(ulid('TASK', 5, b'\x01' * 10), re.compile(f'TASK-{ULID_PATTERN}'))

    def test_a_non_registry_prefix_is_rejected(self):
        for prefix in ('ex', '', 'TOOLONGPREFIX', 'E-X', 7):
            with self.subTest(prefix=prefix), self.assertRaisesRegex(ValueError, 'canonical uppercase registry prefix'):
                ulid(prefix, 1, b'\x00' * 10)

    def test_entropy_must_be_exactly_ten_bytes(self):
        with self.assertRaisesRegex(ValueError, 'ten entropy bytes'):
            ulid('EX', 1, b'\x00' * 9)


if __name__ == '__main__':
    unittest.main()
