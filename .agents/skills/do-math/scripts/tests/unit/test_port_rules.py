"""Port completeness rule (설계 3.3): both implementations carry every protocol operation with one signature."""
from typing import Protocol
import unittest

from support.port_rules import signature_issues


class Thing(Protocol):
    def read(self, path: str) -> bytes: ...
    def write(self, path: str, data: bytes, *, fsync: bool = True) -> None: ...


class Complete:
    def read(self, path: str) -> bytes: return b''
    def write(self, path: str, data: bytes, *, fsync: bool = True) -> None: return None


class Missing:
    def read(self, path: str) -> bytes: return b''


class Drifted:
    def read(self, path: str) -> bytes: return b''
    def write(self, path: str, data: bytes) -> None: return None


class Unannotated:
    def read(self, path): return b''
    def write(self, path, data, *, fsync=True): return None


class SignatureTests(unittest.TestCase):
    def test_annotations_alone_do_not_make_a_signature_differ(self):
        self.assertEqual(signature_issues(Thing, Unannotated(), Complete()), [])

    def test_matching_implementations_have_no_issue(self):
        self.assertEqual(signature_issues(Thing, Complete(), Complete()), [])

    def test_a_missing_operation_is_reported_for_the_side_that_lacks_it(self):
        self.assertEqual(signature_issues(Thing, Complete(), Missing()), [('fake', 'write', 'missing')])

    def test_a_drifted_signature_is_reported(self):
        self.assertEqual(signature_issues(Thing, Drifted(), Complete()), [('real', 'write', 'signature')])


if __name__ == '__main__':
    unittest.main()
