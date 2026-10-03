"""B-46: native usage→실제 수집·수신→execution 저장과 load의 수치 의미를 보존한다."""
import json
import unittest

from do_math.claude_adapter import ADAPTERS
from support.provider_numeric_model import numeric_sim, USAGE


def setUpModule():
    for provider in ADAPTERS:
        numeric_sim(provider)


class NumericUsageTests(unittest.TestCase):
    def test_native_usage_survives_actual_worker_runner_receiver_and_repository(self):
        for provider in ADAPTERS:
            with self.subTest(provider=provider):
                sim = numeric_sim(provider)
                before = set(sim.runtime['executions'])
                sim.engine._enqueue('research_preparation', reason='공급자 사용량 저장 계약')
                sim.engine._save()
                sim.run_until(lambda s: any(eid not in before and row.get('provider_observation')
                    for eid, row in s.runtime['executions'].items()), max_steps=6)
                added = [row for eid, row in sim.runtime['executions'].items() if eid not in before]
                self.assertTrue(added)
                for execution in added:
                    self.assertEqual(execution['status'], 'ended')
                    record = execution['provider_observation']
                    reported = json.loads(record['reported_fields_json'])
                    expected = USAGE if provider == 'codex' else {key: value for key, value in USAGE.items() if key != 'cost_usd'}
                    self.assertEqual(reported['usage'], expected)
                    source = next(row for row in sim.runtime['checkpoints'][execution['id']]['observation_sources']
                        if row['path'] == 'stdout.jsonl')
                    raw = sim.engine.store.read(source['artifact_ref'], sim.engine.head)
                    events = [json.loads(row) for row in raw.splitlines() if row.strip()]
                    self.assertEqual([row['usage'] for row in events if 'usage' in row], [USAGE])
                    self.assertEqual(type(reported['usage']['input_tokens']), int)
                    self.assertEqual(type(reported['usage']['cache_creation_input_tokens']), float)
                    self.assertEqual(record['scope'], 'provider_report_not_remote_termination_or_invoice')
                self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)
