"""10-B B-03: 실제 설치 기록·작업자·공개 trust 소유 흐름의 누적 파일 읽기.

56,230 파일은 원문의 파일 수만 재현한다(8.55GB 내용 재생은 아니다).
이 시나리오는 파일 생성/실제 소유 흐름으로 2초를 넘길 것으로 보아 flows에 둔다.
"""
from collections import Counter
import hashlib
from pathlib import Path
import unittest

import setup_lean
from do_math import file_io, trust_inventory
from do_math.trust_validation import environment_errors
from support.engine_lifecycle import applied, clear_work
from support.provider_probes import ObservedCalls
from support.sim import Sim
from support.storage_files import audit_events
from support.storage_obligations import COST_CASES


class InstallationCosts(unittest.TestCase):
    def test_record_register_and_transition_read_each_judgment_file_once(self):
        for count in COST_CASES['B-03']['sizes']:
            with self.subTest(count=count):
                sim = Sim.activated()
                clear_work(sim)
                root = sim.root / 'cost-toolchain'
                executable = root / 'bin/lean.exe'
                executable.parent.mkdir(parents=True)
                executable.write_bytes(b'external Lean double')
                library = root / 'lib/lean'
                library.mkdir(parents=True)
                raw = b'judgment file scale fixture'
                paths = [library / f'Cost{i:05}.olean' for i in range(count)]
                for path in paths:
                    path.write_bytes(raw)
                expected_paths = {str(path) for path in paths}
                source, _ = trust_inventory.validation_program({'project': None})
                sim.lean.inputs[source.encode('utf-8')] = {}
                with audit_events('open') as opened, ObservedCalls(
                        hashes=file_io.sha256_file, reads=file_io.shared_reader,
                        capture={'hashes': lambda args: str(args['path']),
                                 'reads': lambda args: str(args['path'])}) as calls:
                    result = setup_lean.record_installation([str(executable)], sim.root / 'cost-records',
                        sim.root / 'cost-evidence', jobs=sim.jobs, clock=sim.clock,
                        environment=sim.environment, git_backend=sim.ports.git_backend)
                    self.assertEqual((result['status'], result['created']), ('recorded', True))
                    record = trust_inventory.read_record(result['record_path'])
                    expected = {'toolchain/lib/lean/' + path.name: hashlib.sha256(raw).hexdigest() for path in paths}
                    self.assertEqual(record['baselines'][0]['content']['files'], expected)
                    self.assertEqual(record['baselines'][0]['validation']['status'], 'verified')
                    request = trust_inventory.registration_request(record, result['record_path'], result['binding'])
                    applied(sim, 'trust', config=request)
                    eid = next(key for key, value in sim.instance['trust_environments'].items()
                               if value['toolchain_record']['id'] == result['record_id'])
                    with ObservedCalls(resolve=Path.resolve, hash=file_io.sha256_file,
                                       read=file_io.shared_reader) as structural:
                        begin = len(opened)
                        self.assertEqual(trust_inventory.identity_errors(record['identity']), [])
                        self.assertEqual(environment_errors(sim.instance['trust_environments'][eid],
                                                            sim.runtime['trust_bindings'][eid]), [])
                        structural_opens = opened[begin:]
                    self.assertEqual(structural.count('resolve'), 0)
                    self.assertEqual(structural.count('hash'), 0)
                    self.assertEqual(structural.count('read'), 0)
                    self.assertEqual(structural_opens, [])
                    applied(sim, 'configure', config={'lean_command': [str(executable)]})
                    applied(sim, 'trust', config={'operation': 'transition', 'env_id': eid})
                    sim.run_until(lambda state: state.instance['active_trust_environment'] == eid, max_steps=12)
                    sim.engine.status()
                    _, instance, runtime = sim.engine.store.load()
                    self.assertEqual(instance['active_trust_environment'], eid)
                    self.assertEqual(runtime['trust_bindings'][eid], result['binding'])
                    self.assertEqual(instance['trust_environments'][eid]['validation_receipt']['status'], 'verified')
                # 실행 파일·verifier·작업자 JSON·Lean 입력은 판단 파일 모집단에 속하지 않는다.
                self.assertEqual(Counter(path for path in calls.captured('hashes') if path in expected_paths),
                                 Counter({path: 1 for path in expected_paths}))
                # Windows shared_reader uses CreateFile + fdopen; audit open has an fd, not a path.
                self.assertEqual(Counter(path for path in calls.captured('reads') if path in expected_paths),
                                 Counter({path: 1 for path in expected_paths}))


if __name__ == '__main__':
    unittest.main()
