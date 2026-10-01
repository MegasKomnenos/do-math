"""HTTP port contract (설계 2.2): the urllib transport and the fake answer the same response table alike.

``make(table)`` builds the implementation over ``{path: (status, body, location)}``;
the real side serves the table from a loopback server.
"""
import unittest

from support.fakes.http import make_fake


from support.port_contracts.http import HttpContract

class FakeHttpContract(HttpContract, unittest.TestCase):
    def make(self, table):
        return make_fake(table)


if __name__ == '__main__':
    unittest.main()
