"""Timeline and snapshot status over a persisted snapshot (``reporting.timeline``, ``snapshot_report``), over the real Git process.

Both open the repository themselves with the product's default backend, the
real Git process, and take no Ports; that places these tests with the
boundary tests, as ``test_cli_file_reads`` is placed for ``cli.execute``. The
repository is laid out without a git process (``make_repository``) and written
through the real backend. The legacy continuation test handed ``timeline`` a
free-form runtime through an autospec repository; here the runtime is a stored
state the contract accepts, and the loaded runtime ``timeline`` receives is
held through ``storage_probes.Returns`` to check that it is left unchanged.
"""
import csv
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest

from do_math import activities, execution_lifecycle
from do_math.cli import build_parser, execute
from do_math.repository import ResearchRepository
from do_math.reporting import ASSURANCE, render_human_report, snapshot_report, timeline, timeline_csv
from record_fixtures import stored_surface_state
from support.fakes.clock import FakeClock
from support.fakes.git_backend import make_repository
from support.storage_probes import Returns


class StoredCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = make_repository(Path(temporary.name))
        self.identifier = FakeClock().new_id('RI')
        self.store = ResearchRepository(self.root, self.identifier)

    def surface(self):
        """``stored_surface_state`` owned by this instance: one activity ``AC-1`` and its execution ``EX-1``."""
        instance, runtime = stored_surface_state()
        instance.update(id=self.identifier, workspace=str(self.root / 'workspace'))
        runtime['activities']['AC-1']['owner_ref'] = self.identifier
        return instance, runtime


class ReportingTests(StoredCase):
    def test_claude_usage_projection_survives_git_and_timeline(self):
        from do_math.claude_stream import parse_stream
        from do_math.execution_profiles import execution_observation
        from do_math.payloads import json_safe
        rows = [
            {"type": "system", "subtype": "init", "session_id": "fixture"},
            {"type": "result", "subtype": "success", "is_error": False,
             "session_id": "fixture", "structured_output": {},
             "usage": {"input_tokens": 10, "output_tokens": 5},
             "modelUsage": {"claude-opus-5": {"inputTokens": 10, "costUSD": 0.01}}},
        ]
        raw = b"".join(json.dumps(row).encode() + b"\n" for row in rows)
        parsed = parse_stream(raw)
        self.assertTrue(parsed["turn_completed"])
        keys = ("usage_segments", "model_usage_reported", "usage_scope", "reported_models")
        projected = json_safe({key: parsed[key] for key in keys})
        instance, runtime = self.surface()
        execution = runtime["executions"]["EX-1"]
        execution.update(status="ended", outcome="cancelled",
                         ended_at="2026-09-25T00:00:00Z", usage=parsed["usage_total"], **projected)
        execution["provider_observation"] = execution_observation({
            "provider_observation": {key: parsed[key] for key in keys}})
        head = self.store.initialize(instance, runtime)
        saved = self.store.load(head)[2]["executions"]["EX-1"]
        report = timeline(self.root, self.identifier, snapshot=head)["rows"][0]
        for key in keys:
            self.assertEqual(saved[key], projected[key])
            self.assertEqual(report[key], projected[key])
        self.assertEqual(report["usage"], {"input_tokens": 10, "output_tokens": 5})
        preserved = json.loads(saved["provider_observation"]["reported_fields_json"])
        self.assertEqual(preserved["model_usage_reported"], parsed["model_usage_reported"])
        self.assertEqual(saved["model_usage_reported"]["claude-opus-5"]["costUSD"], {"reported_decimal": "0.01"})

    def test_timeline_preserves_explicit_continuation_and_pending_successor(self):
        instance, runtime = self.surface()
        template = runtime['executions'].pop('EX-1')
        runtime['activities']['AC-1']['assigned_execution_ids'] = []
        # EX-first names no continuation; EX-second continues it, in the execution and in its action.
        for identifier, continuation in (('EX-first', None), ('EX-second', 'EX-first')):
            action = {'id': 'AC-work', 'role': 'research_work', **({'continuation_of': continuation} if continuation else {})}
            execution = {**deepcopy(template), 'id': identifier, 'continuation_of': continuation, 'action': action}
            activities.assign_execution(runtime, 'AC-1', execution)
            execution_lifecycle.transition_execution(execution, 'ended', at='2026-09-20T00:01:00Z', outcome='cancelled')
        pending = {'id': 'AC-work', 'role': 'research_work', 'continuation_of': 'EX-second'}
        runtime['queue'] = [pending, {'id': 'AC-other', 'role': 'maintenance', 'continuation_of': 'EX-unrelated'}]
        head = self.store.initialize(instance, runtime)
        with Returns(ResearchRepository.load, snapshot=deepcopy) as loaded:
            value = timeline(self.root, self.identifier, snapshot=head)
        rows = {row['id']: row for row in value['rows']}
        self.assertIsNone(rows['EX-first']['continuation_of'])
        self.assertEqual(rows['EX-second']['continuation_of'], 'EX-first')
        self.assertEqual(rows['EX-second']['next_actions'], [pending])
        self.assertEqual(rows['EX-first']['next_actions'], [])
        exported = {row['id']: row for row in csv.DictReader(io.StringIO(timeline_csv(value)))}
        self.assertEqual(exported['EX-second']['continuation_of'], 'EX-first')
        self.assertEqual(json.loads(exported['EX-second']['next_actions']), [pending])
        # The state timeline loaded, left unchanged by the projection and the export: it still equals
        # the deep copy taken when load returned it, which no later change of the repository can reach.
        self.assertEqual(len(loaded.values), 1)
        self.assertEqual(loaded.values[0][2]['queue'], runtime['queue'])  # the copy holds the stored state
        self.assertEqual(loaded.values[0], loaded.snapshots[0])

    def test_fixed_snapshot_preserves_unknown_times_and_crosses_the_kst_date(self):
        instance, runtime = self.surface()
        runtime['executions']['EX-1'].update(status='ended',
            action={'id': 'A', 'role': 'research_work', 'lineage_id': 'L'}, model='claude-opus-5',
            created_at='2026-09-18T15:01:02+00:00', ended_at='2026-09-18T15:02:03+00:00', outcome='cancelled')
        head = self.store.initialize(instance, runtime)
        instance['title'] = 'later metadata'
        later = self.store.save_with_state(head, instance, runtime)[0]
        self.assertNotEqual(later, head)
        value = timeline(self.root, self.identifier, snapshot=head)
        self.assertEqual(value['counts_by_unit'], {'internal_execution': 1})
        row = value['rows'][0]
        self.assertEqual(row['created_at_local'], '2026-09-19T00:01:02+09:00')
        self.assertIsNone(row['started_at_utc'])
        self.assertIsNone(row['started_at_local'])
        self.assertEqual(row['lineage_id'], 'L')
        csv_row = next(csv.DictReader(io.StringIO(timeline_csv(value))))
        self.assertEqual(csv_row['started_at_utc'], '')
        args = build_parser().parse_args(['timeline', '--repository', str(self.root), '--instance', self.identifier,
                                          '--snapshot', head, '--format', 'csv'])
        actual, code = execute(args)
        self.assertEqual(code, 0)
        self.assertEqual(actual, timeline_csv(value))


class StatusSnapshotTests(StoredCase):
    def test_snapshot_report_passes_the_requested_areas_to_the_status_projection(self):
        """``snapshot_report`` hands ``requested_areas`` to ``status_report``: record storage alone is healthy, all areas are not."""
        head = self.store.initialize(*self.surface())
        scoped = snapshot_report(self.root, self.identifier, snapshot=head, requested_areas=['record_storage'])
        self.assertEqual(scoped['snapshot'], head)
        self.assertEqual(scoped['inspection']['status'], 'healthy')
        # Without the scope every area is inspected, and the unadopted initial input is incomplete.
        self.assertEqual(snapshot_report(self.root, self.identifier, snapshot=head)['inspection']['status'], 'incomplete')

    def test_json_and_human_status_share_one_snapshot(self):
        head = self.store.initialize(*self.surface())
        budget = {"work-model": {"limit": 1, "used": 0, "execution_ids": []}}
        report = snapshot_report(self.root, self.identifier, snapshot=head, host_observation={
            "budget": budget, "research_observed_at": "2026-09-20T00:00:00Z"})
        self.assertEqual(report["snapshot"], head)
        self.assertEqual(report["goal"], "Prove P")
        self.assertEqual(report["assurance"], ASSURANCE)
        self.assertEqual(report["research_observed_at"], "2026-09-20T00:00:00Z")
        self.assertEqual(report["budget"], budget)
        self.assertIsNone(report["pending_controls"], "an unobserved host field stays unobserved")
        human = render_human_report(report)
        self.assertIn(head, human)
        self.assertIn("inspection:", human)
        self.assertIn("work-model 0/1", human)
        with self.assertRaisesRegex(ValueError, "^status observation has unknown fields: observed_at$"):
            snapshot_report(self.root, self.identifier, snapshot=head,
                            host_observation={"observed_at": "2026-09-20T00:00:00Z"})


if __name__ == '__main__':
    unittest.main()
