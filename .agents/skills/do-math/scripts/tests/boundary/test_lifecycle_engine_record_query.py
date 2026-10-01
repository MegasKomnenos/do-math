"""The record query over a real Git repository (``engine.read_record``): its evidence names the published bytes.

``read_record`` opens the repository itself with the real Git backend, so it
reads what a real ``git`` published; a Sim's Git fake keeps its objects in
memory, where no ``git`` process can read them. The new instance comes from the
public ``initialize`` on the real ports, as the legacy test's did.
"""
import hashlib
from pathlib import Path
import tempfile
import unittest

from do_math.engine import initialize, read_record
from do_math.repository import ResearchRepository
from support.fakes.git_backend import make_repository


class RecordQueryTests(unittest.TestCase):
    def test_a_record_query_returns_evidence_of_the_published_bytes(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = make_repository(root / 'repo')
            identifier = initialize(repository, goal='Prove the stated goal', workspace=root / 'work',
                                    config={'scholarly_enabled': False, 'operator_enabled': False}, codex_home=_entry.codex_home, host_id=_entry.host_id, ports=_entry.ports)['instance_id']
            head, instance, runtime = ResearchRepository(repository, identifier, backend=_entry.ports.git_backend, clock=_entry.ports.clock).load()
            self.assertEqual((runtime['status'], runtime['queue'], instance['grants']), ('initializing', [], {}))
            profile_id = next(iter(instance['execution_profiles']))
            found = read_record(repository, identifier, profile_id, snapshot=head, backend=_entry.ports.git_backend, clock=_entry.ports.clock)
            raw = ResearchRepository(repository, identifier, backend=_entry.ports.git_backend, clock=_entry.ports.clock).read(found['path'], head)
            self.assertEqual(found['sha256'], hashlib.sha256(raw).hexdigest())
            self.assertEqual(found['bytes'], len(raw))
            self.assertEqual(found['snapshot'], head)
            self.assertEqual(found['record']['id'], profile_id)


if __name__ == '__main__':
    unittest.main()
