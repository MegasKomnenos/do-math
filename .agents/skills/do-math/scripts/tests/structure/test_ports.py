"""Every port declared in Ports has its five parts (설계 3.3)."""
import dataclasses
import importlib
import inspect
from pathlib import Path
import unittest

from do_math.ports import Ports
from do_math.wiring import real_ports
from support.port_rules import signature_issues

TESTS = Path(__file__).resolve().parents[1]


def _camel(name):
    return ''.join(part.title() for part in name.split('_'))


class PortCompletenessTests(unittest.TestCase):
    def test_every_port_has_protocol_real_fake_and_both_contract_sides(self):
        from support.entry import entry
        _entry = entry()
        fields = [field.name for field in dataclasses.fields(Ports)]
        self.assertGreater(len(fields), 0)
        real = real_ports(environment=_entry.environment)
        for name in fields:
            with self.subTest(port=name):
                protocol = getattr(importlib.import_module(f'do_math.ports.{name}'), _camel(name))
                fake = importlib.import_module(f'support.fakes.{name}').make_fake()
                self.assertEqual(signature_issues(protocol, getattr(real, name), fake), [])
                contract = getattr(importlib.import_module(f'contracts.test_port_{name}'), _camel(name) + 'Contract')
                for side in ('contracts', 'boundary'):
                    module = importlib.import_module(f'{side}.test_port_{name}')
                    runnable = [value for value in vars(module).values() if inspect.isclass(value)
                                and issubclass(value, contract) and issubclass(value, unittest.TestCase)]
                    self.assertGreaterEqual(len(runnable), 1,
                                            f'{side}.test_port_{name} needs a {contract.__name__} TestCase')


if __name__ == '__main__':
    unittest.main()
