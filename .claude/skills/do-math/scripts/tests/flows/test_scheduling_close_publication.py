"""B-31의 현행 봉인 게시 대기를 공개 bounded run에서 재적용한다."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import setup_lean
from do_math import trust_inventory as records
from support.engine_lifecycle import applied
from support.fakes.host import FakeHost
from support.provider_probes import ObservedCalls
from support.scheduling_return_observer import OwnerProbe
from support.sim import Sim


class PublicationReturnTests(unittest.TestCase):
    def test_bounded_run_applies_previously_sealed_completion_after_rerecord(self):
        with TemporaryDirectory() as directory:
            host = FakeHost()
            sim = Sim.activated(Path(directory), host=host)
            source = 'theorem k : 1 = 1 := rfl'
            sim.lean.allow(source, ['k'], signatures={'k': 'k : 1 = 1'},
                declaration_evidence={'k': {'type': '1 = 1', 'value': None}},
                axioms={'k': []}, dependencies={'k': {}})
            applied(sim, 'knowledge', config={'operation': 'import', 'candidate': {
                'kind': 'theorem', 'title': 'k', 'statement': 'One equals one', 'summary': 'Reflexivity',
                'explanation': 'By reflexivity.', 'lean_code': source,
                'declaration_names': ['k'], 'dependencies': []}})
            environment = sim.instance['trust_environments'][sim.instance['active_trust_environment']]
            host.toolchain_errors = ['approved toolchain file changed']
            def waiting(s):
                return [w for w in s.runtime.get('waiting_actions', {}).values()
                        if w.get('kind') == 'submission_publication']
            sim.run_until(waiting, max_steps=12)
            wait, = waiting(sim)
            eid = wait['execution_id']
            execution = sim.runtime['executions'][eid]
            self.assertEqual(execution['role'], 'identity_review')
            sealed = execution['submission_intent']['output_ref']
            raw = (Path(sim.instance['workspace']) / 'runs' / eid / 'workspace/output.json').read_bytes()
            host.toolchain_errors = []
            # 검사 프로그램의 정확한 바이트 하나만 외부 Lean 응답표에 등록한다.
            # 기록·검증·worker는 setup_lean의 실제 producer를 통과한다.
            program, _ = records.validation_program(environment['toolchain'])
            sim.lean.inputs[program.encode('utf-8')] = {}
            reference = environment['toolchain_record']
            recorded = setup_lean.rerecord(environment['toolchain']['configured_command'],
                Path(reference['path']).parent, sim.root / 'rerecord-evidence', reference['id'],
                identity=environment['toolchain'], jobs=sim.jobs, clock=sim.clock,
                environment=sim.environment, git_backend=sim.ports.git_backend)
            self.assertEqual(recorded['status'], 'recorded')
            before_calls = len(sim.model.calls)
            with OwnerProbe(sim) as probe, ObservedCalls(receive=sim.engine._receive_submission) as calls:
                answer = sim.engine.run(max_steps=1)
            self.assertIsInstance(answer, dict)
            self.assertEqual(probe.failures, [])
            self.assertNotIn(wait['action']['id'], sim.runtime.get('waiting_actions', {}))
            self.assertEqual(sim.runtime['executions'][eid]['outcome'], 'output_accepted')
            self.assertEqual(sim.engine.store.read(sealed, sim.engine.head), raw)
            received = [args['execution_id'] for args in calls.captured('receive')]
            self.assertEqual(received.count(eid), 1)
            self.assertEqual([c['action']['id'] for c in sim.model.calls[before_calls:]
                              if c['action']['id'] == wait['action']['id']], [])
            stored = sim.engine.store.load(sim.engine.head)[2]
            self.assertEqual(stored['executions'][eid], sim.runtime['executions'][eid])
