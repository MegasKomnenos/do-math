"""Focused contract tests for the one-step, centrally sealed submission flow."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from do_math import contracts, execution_lifecycle, submission
from do_math.engine import ResearchEngine
from do_math.context_store import collect_outputs
from do_math.control_transport import ControlTransport
from do_math.git_store import GitStateStore
from do_math.repository import canonical_json
from research_fixtures import seal_response


class SubmissionFlowTests(unittest.TestCase):
    def test_real_preview_entry_accepts_questions_without_publishing(self):
        from test_static_review_repairs import context_engine
        root = Path(self.temporary.name)
        workspace = root / 'runs' / 'EX-flow' / 'workspace'
        workspace.mkdir(parents=True)
        engine = context_engine()
        engine.instance['workspace'] = str(root)
        action = {'id': 'AC-flow', 'role': 'maintenance'}
        execution = {'id': 'EX-flow', 'role': 'maintenance', 'status': 'running',
                     'action': action, 'input_bundle': 'BA-preview'}
        engine.runtime['executions']['EX-flow'] = execution
        context = {**deepcopy(self.context), 'action': action, 'snapshot': engine.head,
                   'workspace': str(workspace)}
        context.pop('submission_contract', None)
        submission.install_tools(workspace, context, self.schema, None)
        output = {**self.output, 'questions': ['What should operations decide?']}
        seal_response(output, context, workspace)
        draft = workspace / 'draft.json'
        draft.write_bytes(canonical_json(output))
        base = 'runtime/artifacts/BA-preview'
        input_bytes = canonical_json(context)
        schema_bytes = canonical_json(self.schema)
        def read(path, snapshot):
            if path == base + '/input/submission/context.json':
                return input_bytes
            if path == base + '/schema.json':
                return schema_bytes
            raise AssertionError('preview read an unpublished artifact from Git: ' + path)
        engine.store.read.side_effect = read
        engine._validate_bundle_current = lambda *args, **kwargs: None
        before = canonical_json(engine.runtime)
        (workspace / 'activity-extensions.json').write_bytes(b'{"knowledge_changes": []}')
        preview = engine._preview_submission(execution, {'draft_path': 'draft.json'})
        self.assertTrue(preview['passed'], preview['issues'])
        self.assertEqual(canonical_json(engine.runtime), before)
        self.assertNotIn('artifact_bundle', engine.runtime['executions']['EX-flow'])
        engine.store.validate_candidate.assert_called_once()
        self.assertFalse(engine.runtime['question_links'])
        invalid = {**output, 'used_sources': ['TK-not-in-input']}
        seal_response(invalid, context, workspace)
        draft.write_bytes(canonical_json(invalid))
        rejected = engine._preview_submission(execution, {'draft_path': 'draft.json'})
        self.assertFalse(rejected['passed'])
        self.assertEqual(canonical_json(engine.runtime), before)
        engine.store.validate_candidate.assert_called_once()

    def test_central_candidate_is_read_from_its_git_receipt_without_legacy_fields(self):
        sealed = submission.seal_submission(self.workspace, '.scratch/draft.json',
            execution_id='EX-flow', context=self.context, schema=self.schema,
            max_artifact_bytes=1024 * 1024)
        self.assertTrue(sealed['passed'], sealed['check']['issues'])
        prefix = 'runtime/artifacts/BA-central/submission'
        artifacts = {prefix + '/' + path: raw for path, raw in sealed['artifacts'].items()}
        intent = {**sealed['intent'], 'output_ref': prefix + '/output.json',
                  'extensions_ref': prefix + '/extensions.json', 'check_ref': prefix + '/check.json'}
        receipt = {'state': 'accepted', 'execution_id': 'EX-flow', 'payload': {'submission_check': {
            'artifacts': [{'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
                          for path, raw in artifacts.items()]}}}
        execution = {'id': 'EX-flow', 'submission_intent': intent, 'submission_receipt': receipt}
        repo = Path(self.temporary.name) / 'repo'
        repo.mkdir()
        subprocess.run(['git', '-C', str(repo), 'init', '-q'], check=True)
        store = GitStateStore(repo, 'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV')
        head = store.publish(None, {'research/fixture.json': b'{}', **artifacts}).head
        recovered = submission.read_sealed_submission(execution, head,
            lambda snapshot, path: store.read_bytes(snapshot, path))
        self.assertEqual(recovered['output'], self.output)
        self.assertEqual(recovered['extensions'], {})
        self.assertTrue(recovered['check']['passed'])

        for mutation in ('output', 'extensions', 'execution', 'mode', 'schema'):
            with self.subTest(mutation=mutation):
                changed = dict(artifacts)
                changed_intent = deepcopy(intent)
                changed_check = deepcopy(sealed['check'])
                if mutation == 'output':
                    changed[intent['output_ref']] = canonical_json({
                        **self.output, 'report': 'A different, unchecked report'})
                elif mutation == 'extensions':
                    changed[intent['extensions_ref']] = canonical_json({
                        'research_insights': [{'kind': 'question', 'title': 'New question',
                            'statement': 'What remains?', 'summary': 'Unchecked insight'}]})
                elif mutation == 'execution':
                    changed_check['execution_id'] = 'EX-other'
                elif mutation == 'mode':
                    changed_check['mode'] = 'producer'
                else:
                    changed_check['schema_ref']['sha256'] = '0' * 64
                changed_check['id'] = 'MC-' + submission.integration.digest({
                    key: value for key, value in changed_check.items() if key != 'id'})[:24]
                changed[intent['check_ref']] = canonical_json(changed_check)
                for field in ('output', 'extensions'):
                    changed_intent[field + '_sha256'] = hashlib.sha256(
                        changed[intent[field + '_ref']]).hexdigest()
                changed_receipt = deepcopy(receipt)
                changed_receipt['payload']['submission_check']['artifacts'] = [
                    {'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
                    for path, raw in changed.items()]
                with self.assertRaises(submission.SealedSubmissionError):
                    submission.read_sealed_submission(
                        {'id': 'EX-flow', 'submission_intent': changed_intent,
                         'submission_receipt': changed_receipt},
                        head, lambda snapshot, path: changed[path])

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name) / "workspace"
        self.workspace.mkdir()
        self.delivery = Path(self.temporary.name) / "delivery"
        self.transport = ControlTransport(self.delivery)
        self.binding = self.transport.issue("EX-flow", "GR-flow", workspace=self.workspace)
        self.context = {
            "action": {"role": "maintenance", "id": "AC-flow"},
            "execution_id": "EX-flow",
            "control_binding": self.binding,
            "snapshot": "fixed",
            "tasks": [],
            "knowledge_catalog": [],
            "sources": [],
            "kind_definitions": {},
        }
        self.schema = contracts.schema_for("maintenance")
        submission.install_tools(self.workspace, self.context, self.schema, None)
        self.output = {
            "summary": "Inspect only",
            "used_sources": [],
            "questions": [],
            "report": "Inspected",
            "remaining_work": [],
        }
        seal_response(self.output, self.context, self.workspace)
        self.draft = self.workspace / ".scratch" / "draft.json"
        self.draft.parent.mkdir()
        self.draft.write_bytes(canonical_json(self.output))

    def test_central_seal_uses_actual_bytes_and_survives_original_draft_change(self):
        sealed = submission.seal_submission(
            self.workspace, ".scratch/draft.json", execution_id="EX-flow",
            context=self.context, schema=self.schema, max_artifact_bytes=1024 * 1024)
        self.assertTrue(sealed["passed"], sealed["check"]["issues"])
        original = self.draft.read_bytes()
        self.draft.write_bytes(canonical_json({"changed": True}))
        self.assertEqual(original, sealed["artifacts"]["output.json"])
        self.assertEqual(self.output, submission.load_json(sealed["artifacts"]["output.json"]))
        self.assertNotIn(".control/stop-request.json", {row["path"] for row in sealed["manifest"]})

    def test_central_capture_never_mixes_checked_draft_with_a_later_file_version(self):
        draft = self.workspace / "draft.json"
        draft.write_bytes(canonical_json(self.output))
        original_collect = submission.collect_outputs
        calls = []

        def racing_collect(*args, **kwargs):
            calls.append(True)
            changed = deepcopy(self.output)
            changed["report"] = "The draft changed during central capture."
            draft.write_bytes(canonical_json(changed))
            return original_collect(*args, **kwargs)

        with patch.object(submission, "collect_outputs", racing_collect):
            sealed = submission.seal_submission(
                self.workspace, "draft.json", execution_id="EX-flow",
                context=self.context, schema=self.schema, max_artifact_bytes=1024 * 1024)
        self.assertTrue(sealed["passed"], sealed["check"]["issues"])
        self.assertEqual(1, len(calls))
        self.assertEqual(sealed["artifacts"]["output.json"], sealed["artifacts"]["files/draft.json"])

    def test_submit_transport_contains_only_the_draft_locator(self):
        with patch.object(ControlTransport, "worker_submit", return_value={"state": "submitted"}) as submit:
            submission.request_control(self.workspace, ".scratch/draft.json", kind="submit_intent", wait_seconds=0,
                                       binding=self.binding)
        payload = submit.call_args.kwargs["payload"]
        self.assertEqual({"draft_path": ".scratch/draft.json"}, payload)

    def test_control_changes_do_not_change_candidate_hashes_or_output_manifest(self):
        first = submission.producer_check(self.workspace, self.draft)
        before = collect_outputs(self.workspace, max_bytes=1024 * 1024)["manifest"]
        control = self.workspace / ".control"
        control.mkdir()
        (control / "stop-request.json").write_bytes(canonical_json({"reason": "submission_intent"}))
        second = submission.producer_check(self.workspace, self.draft)
        after = collect_outputs(self.workspace, max_bytes=1024 * 1024)["manifest"]
        self.assertEqual(first["input_hashes"], second["input_hashes"])
        self.assertEqual(before, after)

    def test_lifecycle_accepts_only_central_sealed_candidate_not_worker_manifest(self):
        execution = execution_lifecycle.create_execution(
            execution_id="EX-flow", owner_activity_id="AY-flow", actor_kind="ai",
            input_manifest={}, profile_ref={}, created_at="2026-09-21T00:00:00+00:00")
        execution_lifecycle.transition_execution(execution, "starting", at="2026-09-21T00:00:01+00:00")
        execution_lifecycle.transition_execution(execution, "running", at="2026-09-21T00:00:02+00:00")
        intent = {"candidate_id": "CS-one", "output_ref": "runtime/artifacts/BA-one/submission/output.json"}
        receipt = {"id": "CT-one", "kind": "submit_intent", "state": "accepted",
                   "execution_id": "EX-flow", "received_at": "2026-09-21T00:00:03+00:00"}
        execution_lifecycle.record_submission_intent(execution, intent, receipt)
        self.assertEqual("stopping", execution["status"])
        self.assertEqual(intent, execution["submission_intent"])

    def test_stopped_provider_recovers_the_frozen_submission_without_reading_original(self):
        sealed = submission.seal_submission(
            self.workspace, ".scratch/draft.json", execution_id="EX-flow",
            context=self.context, schema=self.schema, max_artifact_bytes=1024 * 1024)
        raw = sealed["artifacts"]["output.json"]
        self.draft.write_bytes(canonical_json({"changed": True}))
        engine = object.__new__(ResearchEngine)
        engine.head = "sealed-head"
        engine.runtime = {"status": "running"}
        engine.instance = {"lifecycle": {"state": "active"}}
        engine._clock_guard = unittest.mock.Mock(return_value={"usable": True})
        engine.store = unittest.mock.Mock()
        engine.store.read.return_value = raw
        execution = {"id": "EX-flow", "action": deepcopy(self.context["action"]),
            "submission_intent": {"output_ref": "sealed/output.json",
            "output_sha256": hashlib.sha256(raw).hexdigest()}}
        recovered = engine._collect_submitted_result(execution,
            {"status": "stopped", "usage": {}}, self.context, self.schema, self.workspace)
        self.assertEqual("completed", recovered["status"])
        self.assertEqual("sealed_submission", recovered["collection"])
        self.assertEqual(self.output, recovered["output"])

    def test_result_file_recovery_uses_the_receipt_snapshot_not_live_workspace(self):
        research = self.workspace / "research.txt"
        research.write_bytes(b"accepted bytes")
        sealed = submission.seal_submission(
            self.workspace, ".scratch/draft.json", execution_id="EX-flow",
            context=self.context, schema=self.schema, max_artifact_bytes=1024 * 1024)
        research.write_bytes(b"later mutation")
        engine = object.__new__(ResearchEngine)
        engine.head = "sealed-head"
        by_ref = {"sealed/files/" + row["path"]: sealed["artifacts"]["files/" + row["path"]]
                  for row in sealed["manifest"]}
        engine.store = unittest.mock.Mock()
        engine.store.read.side_effect = lambda ref, _head: by_ref[ref]
        execution = {"submission_intent": {"file_refs": [
            {**row, "artifact_ref": "sealed/files/" + row["path"]} for row in sealed["manifest"]]}}
        recovered = engine._sealed_submission_files(execution)
        self.assertEqual(b"accepted bytes", recovered["files"]["research.txt"])

    def test_illegal_draft_reference_is_rejected_before_transport(self):
        outside = self.workspace.parent / "outside.json"
        outside.write_bytes(canonical_json(self.output))
        sealed = submission.seal_submission(
            self.workspace, "../outside.json", execution_id="EX-flow",
            context=self.context, schema=self.schema, max_artifact_bytes=1024 * 1024)
        self.assertFalse(sealed["passed"])
        self.assertTrue(any(row["rule_id"] == "submission.read"
                            for row in sealed["check"]["issues"]))

    def test_central_candidate_rejects_missing_workspace_reference(self):
        output = {**self.output, "used_sources": ["workspace:missing-evidence.txt"]}
        seal_response(output, self.context, self.workspace)
        self.draft.write_bytes(canonical_json(output))
        sealed = submission.seal_submission(
            self.workspace, ".scratch/draft.json", execution_id="EX-flow",
            context=self.context, schema=self.schema, max_artifact_bytes=1024 * 1024)
        self.assertFalse(sealed["passed"])
        self.assertTrue(any(row["path"] == "output/used_sources/0" and "preserved workspace file" in row["message"]
                            for row in sealed["check"]["issues"]), sealed["check"]["issues"])

    def test_empty_known_extension_is_normalized_at_capture_and_sealed_read(self):
        raw = b'{ "knowledge_changes": [] }\r\n'
        (self.workspace / "activity-extensions.json").write_bytes(raw)
        producer = submission.producer_check(self.workspace, self.draft)
        self.assertTrue(producer["passed"], producer["issues"])
        sealed = submission.seal_submission(self.workspace, ".scratch/draft.json",
            execution_id="EX-flow", context=self.context, schema=self.schema,
            max_artifact_bytes=1024 * 1024)
        self.assertTrue(sealed["passed"], sealed["check"]["issues"])
        self.assertEqual(producer["input_hashes"], sealed["check"]["input_hashes"])
        self.assertEqual(sealed["artifacts"]["extensions.json"], raw)
        self.assertEqual(sealed["artifacts"]["files/activity-extensions.json"], raw)
        prefix = "runtime/artifacts/BA-empty/"
        artifacts = {prefix + name: data for name, data in sealed["artifacts"].items()}
        intent = {**sealed["intent"], "output_ref": prefix + "output.json",
                  "extensions_ref": prefix + "extensions.json", "check_ref": prefix + "check.json"}
        receipt = {"state": "accepted", "execution_id": "EX-flow", "payload": {"submission_check": {
            "artifacts": [{"path": path, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
                          for path, data in artifacts.items()]}}}
        recovered = submission.read_sealed_submission(
            {"id": "EX-flow", "submission_intent": intent, "submission_receipt": receipt},
            "fixed", lambda snapshot, path: artifacts[path])
        self.assertEqual(recovered["extensions"], {})
        for invalid in ({"unknown_family": []}, {"knowledge_changes": {}},
                        {"knowledge_changes": [{"id": "KN-unavailable"}]}):
            with self.subTest(invalid=invalid):
                (self.workspace / "activity-extensions.json").write_bytes(canonical_json(invalid))
                rejected = submission.seal_submission(self.workspace, ".scratch/draft.json",
                    execution_id="EX-flow", context=self.context, schema=self.schema,
                    max_artifact_bytes=1024 * 1024)
                self.assertFalse(rejected["capture_eligible"])

    def test_central_candidate_rejects_malformed_draft_bytes(self):
        self.draft.write_bytes(b'{"summary":')
        sealed = submission.seal_submission(
            self.workspace, ".scratch/draft.json", execution_id="EX-flow",
            context=self.context, schema=self.schema, max_artifact_bytes=1024 * 1024)
        self.assertFalse(sealed["passed"])
        self.assertTrue(any(row["rule_id"] == "submission.parse"
                            for row in sealed["check"]["issues"]))


class CentralSubmissionHistoryTests(unittest.TestCase):
    def setUp(self):
        # A saved, approved synthetic research state; no model or Lean call.
        from test_input_recovery import InputRecoveryPublicTests
        InputRecoveryPublicTests.setUp(self)
        self.engine = ResearchEngine(self.repo, self.identifier)
        action = {'id': 'AC-history', 'role': 'maintenance'}
        self.engine._action_lifecycle_gate(action)
        execution = self.engine._register_execution(action,
            {'id': 'EX-history', 'role': 'maintenance', 'status': 'running'})
        execution.update(grant_id=action['grant_id'], input_bundle='BA-history-input', input_snapshot=self.engine.head)
        from do_math.planning import governance_revisions
        execution.update(governance_revisions(self.engine.instance))
        self.workspace = Path(self.engine.instance['workspace']) / 'runs/EX-history/workspace'
        self.workspace.mkdir(parents=True)
        self.context = {'action': action, 'execution_id': execution['id'], 'snapshot': self.engine.head,
            'tasks': [], 'knowledge_catalog': [], 'sources': [], 'kind_definitions': {},
            'grants': [deepcopy(self.engine.instance['grants'][action['grant_id']])]}
        self.schema = contracts.schema_for('maintenance')
        submission.install_tools(self.workspace, self.context, self.schema, 1024*1024)
        self.engine._save({'runtime/artifacts/BA-history-input/input/submission/context.json': canonical_json(self.context),
                          'runtime/artifacts/BA-history-input/schema.json': canonical_json(self.schema)})
        self.transport = ControlTransport(self.root/'delivery')
        self.binding = self.transport.issue('EX-history', action['grant_id'], workspace=self.workspace)
        self.output = {'summary': 'Exact e\u0301 diagnostic', 'used_sources': [], 'questions': [],
                      'report': 'Actual central receipt test; no mathematical approval.', 'remaining_work': []}
        seal_response(self.output, self.context, self.workspace)

    def submit(self, request_id, raw):
        (self.workspace/'draft.json').write_bytes(raw)
        request = {**self.binding, 'request_id': request_id, 'kind': 'submit_intent',
                   'payload': {'draft_path': 'draft.json'}}
        return request, self.transport.receive(request, publish=self.engine._publish_control_request)

    def test_orphan_impact_is_returned_then_default_bundle_preserves_raw_git_input(self):
        from do_math import integration
        action = self.context["action"]
        bad = deepcopy(self.output)
        bad["integration_bundles"][0]["impact_set"] = ["read-source"]
        _, rejected = self.submit("CT-impact", canonical_json(bad))
        self.assertEqual(rejected["state"], "rejected", rejected)
        self.assertEqual(self.engine.runtime["executions"]["EX-history"]["status"], "running")
        summary = self.engine._submission_check_summary(self.engine.head, self.engine.runtime)
        self.assertTrue(any(row["rule_id"] == "integration.mutation_root" for row in summary["unresolved"]), summary)
        output = {k: v for k, v in self.output.items() if k != "integration_bundles"}
        output["report"] = "조합 e\u0301 · é · 한글 · 😀\n exact original"
        raw = json.dumps(output, ensure_ascii=False, indent=3).encode("utf-8")
        _, accepted = self.submit("CT-default", raw)
        self.assertEqual(accepted["state"], "accepted", accepted)
        self.engine = ResearchEngine(self.repo, self.identifier)
        execution = self.engine.runtime["executions"]["EX-history"]
        stored = self.engine.store.read(execution["submission_intent"]["output_ref"], self.engine.head)
        self.assertEqual(stored, raw)
        restored = submission.load_json(stored)
        self.assertNotIn("integration_bundles", restored)
        fixed = submission.load_json(self.engine.store.read(
            "runtime/artifacts/BA-history-input/input/submission/context.json", self.engine.head))
        before = list(integration.split_bundles(output, {}, self.context))
        after = list(integration.split_bundles(restored, {}, fixed))
        self.assertEqual(before, after)
        self.assertEqual(len(after), 1)
        self.assertEqual(after[0]["authority_refs"], [action["grant_id"]])
        result = self.engine._apply_submission_bundles(action, restored, {}, "EX-history", fixed, [])
        self.assertEqual(result["status"], "accepted", result["issues"])
        self.assertEqual(len(result["bundles"]), 1)
        _, _, saved = self.engine.store.load()
        self.assertIn(after[0]["integration_id"], saved["integrations"])
        self.assertEqual(self.engine.store.read(execution["submission_intent"]["output_ref"], self.engine.head), raw)

    def test_rejected_corrected_replayed_and_snapshot_bound_central_checks(self):
        bad = canonical_json({k:v for k,v in self.output.items() if k != 'report'})
        request, rejected = self.submit('CT-bad', bad)
        self.assertEqual(rejected['state'], 'rejected', rejected)
        self.assertTrue(rejected.get('publication_id'), rejected)
        first_head = self.engine.head
        self.assertEqual(self.engine.runtime['executions']['EX-history']['status'], 'running')
        self.assertNotIn('authority_revocation', self.engine.runtime['executions']['EX-history'])
        first = self.engine._submission_check_summary(first_head, self.engine.runtime)
        self.assertEqual(first['status'], 'verified', first)
        self.assertEqual(first['seal_count'], 1)
        self.assertTrue(first['unresolved'])
        stored = next(r for r in self.engine.runtime['control_receipts'].values() if r['request_id']=='CT-bad')
        evidence = stored['payload']['submission_check']
        draft = next(r for r in evidence['artifacts'] if r['path'].endswith('/output.json'))
        self.assertEqual(self.engine.store.read(draft['path'], first_head), bad)
        self.assertEqual(hashlib.sha256(bad).hexdigest(), draft['sha256'])
        # Restart/replay reads the original receipt even after local bytes change.
        self.engine = ResearchEngine(self.repo, self.identifier)
        (self.workspace/'draft.json').write_bytes(b'{changed local bytes')
        replay = self.engine._publish_control_request(request)
        self.assertEqual(replay['state'], 'rejected')
        self.assertEqual(self.engine.head, first_head)
        self.assertEqual(replay['result'], rejected['result'])
        # Optional local history is neither authority nor a submission prerequisite.
        (self.workspace/'checks').mkdir(exist_ok=True)
        (self.workspace/'checks/broken.json').write_bytes(b'{broken optional history')
        _, accepted = self.submit('CT-good', canonical_json(self.output))
        self.assertEqual(accepted['state'], 'accepted', accepted)
        final = self.engine._submission_check_summary(self.engine.head, self.engine.runtime)
        self.assertEqual(final['status'], 'verified', final)
        self.assertEqual(final['seal_count'], 2)
        self.assertEqual(final['unresolved'], [])
        self.assertEqual(sum(final['rule_failure_counts'].values()), sum(first['rule_failure_counts'].values()))
        self.assertEqual(self.engine.runtime['executions']['EX-history']['status'], 'stopping')
        _, _, earlier = self.engine.store.load(first_head)
        self.assertEqual(self.engine._submission_check_summary(first_head, earlier), first)
        replay = self.engine._publish_control_request({**self.binding,'request_id':'CT-good',
            'kind':'submit_intent','payload':{'draft_path':'draft.json'}})
        self.assertEqual(replay['state'], 'accepted')
        self.assertEqual(self.engine._submission_check_summary(self.engine.head,self.engine.runtime)['seal_count'],2)
        missing = deepcopy(self.engine.runtime)
        missing['events'] = [r for r in missing['events'] if r['kind']!='submission_checked']
        self.assertEqual(self.engine._submission_check_summary(self.engine.head,missing)['status'],'incomplete')
        with self.assertRaisesRegex(ValueError, 'immutable'):
            self.engine.store._store.publish(self.engine.head, {draft['path']: b'tampered'})
        read = self.engine.store.read
        with patch.object(self.engine.store,'read',side_effect=lambda path,head:
                          b'tampered' if path==draft['path'] else read(path,head)):
            self.assertEqual(self.engine._submission_check_summary(self.engine.head,self.engine.runtime)['status'],'incomplete')

if __name__ == "__main__":
    unittest.main()
