"""Review publication and public dialogue on real stored review cycles."""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import unittest

from do_math import knowledge_records
from do_math.engine import ResearchEngine
from do_math.git_store import GitStateStoreConflict
from do_math.local_host import LocalHost
from do_math.observations import ObservationTracker
from support.provider_live import batch, running_execution
from support.provider_probes import ObservedCalls
from support.review_sim import opened_sim, reviewed_sim, cycle_of
from support.storage_records import held_ref_lock


def setUpModule():
    opened_sim()
    reviewed_sim()


class PublicationTrustIdentityTests(unittest.TestCase):
    def test_changed_identity_blocks_match_publication_but_olean_metadata_is_not_rechecked(self):
        sim = reviewed_sim()
        ports = replace(sim.ports, host=LocalHost(jobs=sim.jobs, clock=sim.clock, environment=sim.environment))
        engine = ResearchEngine(sim.repository, sim.instance_id, ports=ports, codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
        cycle = deepcopy(cycle_of(sim))
        row = next(e for e in engine.runtime['executions'].values() if e['role'] == 'identity_review')
        action = row['action']
        environment = engine.instance['trust_environments'][engine.instance['active_trust_environment']]
        compiler = Path(environment['toolchain']['executable'])
        olean = compiler.parents[1] / 'lib/lean/Init/Prelude.olean'
        compiler_raw, olean_raw = compiler.read_bytes(), olean.read_bytes()
        try:
            with ObservedCalls(publish=knowledge_records.record_identity_assessment) as calls:
                engine._publish_identity_review_result(action, deepcopy(cycle), row['id'])
                engine._save()
                self.assertEqual(calls.count('publish'), 1)
                olean.write_bytes(b'changed module after the formal check')
                engine._publish_identity_review_result(action, deepcopy(cycle), row['id'])
                engine._save()
                self.assertEqual(calls.count('publish'), 2)
                compiler.write_bytes(b'changed compiler')
                with self.assertRaisesRegex(ValueError, 'current trust identity required: approved toolchain file changed'):
                    engine._publish_identity_review_result(action, deepcopy(cycle), row['id'])
                self.assertEqual(calls.count('publish'), 2)
        finally:
            compiler.write_bytes(compiler_raw)
            olean.write_bytes(olean_raw)


class ReviewDialogueObservationTests(unittest.TestCase):
    def test_review_public_dialogue_keeps_raw_row_order_and_retries_after_failed_cas(self):
        sim = opened_sim()
        action = next(a for a in sim.runtime['queue'] if a['role'] == 'identity_review')
        workspace = running_execution(sim, 'EX-review', 'identity_review', action=deepcopy(action))
        stream = workspace.parent / 'evidence/stdout.jsonl'
        stream.parent.mkdir(exist_ok=True)
        event = {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'Visible independent judgment'}}
        tail = {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'Final unterminated public message'}}
        row = json.dumps(event).encode() + b'\n'
        tail_row = json.dumps(tail).encode()
        stream.write_bytes(b'\n' + row + tail_row)
        tracker = ObservationTracker('EX-review', workspace,
            {'observation_mode': 'deadline_only', 'research_self_checks': False}, time_port=sim.clock)
        first = batch(sim, [event], stream, start=1, rows=[row], first_row=0)
        head = sim.engine.head
        with ObservedCalls(record=type(sim.engine)._record_review_observation) as calls:
            with held_ref_lock(sim.engine.store), self.assertRaisesRegex(GitStateStoreConflict, 'compare-and-swap'):
                sim.engine._observe_running('EX-review', tracker, first)
            self.assertEqual(sim.engine.head, head)
            sim.engine._observe_running('EX-review', tracker, first)
            captured = calls.captured('record')[-1]
            self.assertEqual((captured['execution_id'], captured['event'], captured['event_index']), ('EX-review', event, 0))
            self.assertEqual(sim.engine.store.read(captured['artifact_ref'], sim.engine.head), row)
            sim.engine._observe_running('EX-review', tracker,
                batch(sim, [tail], stream, start=1 + len(row), rows=[tail_row], first_row=1, terminated=True))
            captured = calls.captured('record')[-1]
            self.assertEqual((captured['execution_id'], captured['event'], captured['event_index']), ('EX-review', tail, 1))
            self.assertEqual(sim.engine.store.read(captured['artifact_ref'], sim.engine.head), tail_row)
        messages = [r for r in cycle_of(sim)['turns'][action['slot']] if r['kind'] == 'observed_public_message']
        self.assertEqual([r['source']['event_index'] for r in messages], [0, 1])
        self.assertEqual([r['content'] for r in messages], [event['item']['text'], tail['item']['text']])
