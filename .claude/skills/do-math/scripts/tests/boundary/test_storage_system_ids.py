"""New identifiers from the real system clock and random source (``system_clock.new_id``, a boundary adapter).

``SystemClock.new_id`` is judged by the clock port contract
(``boundary/test_port_clock.py``); the module function ``new_id``, which the
scheduled operator still calls, is a separate function over the same real
sources, so its shape is fixed here against the literal Crockford alphabet.
"""
import re
import unittest

from do_math.system_clock import new_id


class SystemIdTests(unittest.TestCase):
    def test_new_id_is_canonical_ulid(self):
        self.assertRegex(new_id('RI'), re.compile(r'^RI-[0-7][0-9A-HJKMNP-TV-Z]{25}$'))


if __name__ == '__main__':
    unittest.main()
