"""The centrally sealed submission flow: sealing, capture, preview, bundle application, receipts and publication waits."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import uuid
from copy import deepcopy
from pathlib import Path
from unittest.mock import create_autospec, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import contracts, execution_lifecycle, integration, knowledge_io, submission
from do_math.context_store import collect_outputs
from do_math.control_transport import ControlTransport
from do_math.engine import ResearchEngine
from do_math.git_store import GitStateStore
from do_math.repository import canonical_json, exact_content_hash, ResearchRepository
from engine_fixtures import (approve_contract, native_result, routing_engine, start_submission_history,
                             submit_history)
from knowledge_fixtures import knowledge_candidate
from research_fixtures import bare_engine, git_init, seal_response


class SubmissionFlowTests(unittest.TestCase):
    def test_issued_input_is_parsed_once_per_content_and_returned_as_copies(self):
        import uuid
        reads = []
        # A nonce keeps these bytes apart from memo entries other tests left in the process.
        nonce = uuid.uuid4().hex
        def read(path, snapshot):
            reads.append(path)
            # Every bundle holds the same bytes for the same file name.
            return canonical_json({'file': path.rsplit('/', 1)[-1], 'nonce': nonce})
        execution = {'input_bundle': 'BA-' + uuid.uuid4().hex}
        with patch.object(submission, 'load_json', wraps=submission.load_json) as parse:
            first, _ = submission.issued_input(execution, 'head', read)
            first['changed'] = True
            second, schema = submission.issued_input(execution, 'head', read)
            # The bytes are read on every call; each content is parsed once.
            self.assertEqual(reads, ['runtime/artifacts/' + execution['input_bundle'] + '/' + name
                                     for name in ('input/submission/context.json', 'schema.json')] * 2)
            self.assertEqual(parse.call_count, 2)
            self.assertNotIn('changed', second)
            self.assertEqual(schema['file'], 'schema.json')
            schema['changed'] = True
            # The same bytes under another bundle and snapshot reuse the parse, as copies.
            other, other_schema = submission.issued_input({'input_bundle': 'BA-' + uuid.uuid4().hex}, 'other', read)
            self.assertEqual(parse.call_count, 2)
            self.assertEqual(other, second)
            self.assertNotIn('changed', other_schema)
            # Different bytes are parsed again.
            nonce = uuid.uuid4().hex
            third, _ = submission.issued_input(execution, 'head', read)
            self.assertEqual(parse.call_count, 4)
            self.assertEqual(third['nonce'], nonce)

    def test_real_preview_entry_accepts_questions_without_publishing(self):
        from engine_fixtures import context_engine
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
        engine._validate_bundle_current = create_autospec(engine._validate_bundle_current, return_value=None)
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
        git_init(repo)
        store = GitStateStore(repo, 'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV')
        head = store.publish(None, {'research/fixture.json': b'{}', **artifacts}).head
        recovered = submission.read_sealed_submission(execution, head,
            lambda path, snapshot: store.read_bytes(snapshot, path))
        self.assertEqual(recovered['output'], self.output)
        self.assertEqual(recovered['extensions'], {})
        # With the repository identity, a sealed row is hashed once per process (이음새-정본.md §3).
        from unittest.mock import Mock, patch
        read = lambda path, snapshot: store.read_bytes(snapshot, path)
        self.assertEqual(submission.read_sealed_submission(execution, head, read, git_dir=store.git_dir), recovered)
        with patch.object(submission, 'hashlib', Mock(sha256=Mock(side_effect=AssertionError('sealed row rehashed')))):
            self.assertEqual(submission.read_sealed_submission(execution, head, read, git_dir=store.git_dir), recovered)
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
                changed_check['id'] = 'MC-' + exact_content_hash({
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
                        head, lambda path, snapshot: changed[path])

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
        engine = bare_engine({"lifecycle": {"state": "active"}}, {"status": "running"}, head="sealed-head",
                             store=create_autospec(ResearchRepository, instance=True))
        engine._clock_guard = create_autospec(engine._clock_guard, return_value={"usable": True})
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
        engine = bare_engine(head="sealed-head", store=create_autospec(ResearchRepository, instance=True))
        by_ref = {"sealed/files/" + row["path"]: sealed["artifacts"]["files/" + row["path"]]
                  for row in sealed["manifest"]}
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
            "fixed", lambda path, snapshot: artifacts[path])
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
        start_submission_history(self)

    def test_orphan_impact_is_returned_then_default_bundle_preserves_raw_git_input(self):
        from do_math import integration
        action = self.context["action"]
        bad = deepcopy(self.output)
        bad["integration_bundles"][0]["impact_set"] = ["read-source"]
        _, rejected = submit_history(self, "CT-impact", canonical_json(bad))
        self.assertEqual(rejected["state"], "rejected", rejected)
        self.assertEqual(self.engine.runtime["executions"]["EX-history"]["status"], "running")
        summary = self.engine._submission_check_summary(self.engine.head, self.engine.runtime)
        self.assertTrue(any(row["rule_id"] == "integration.mutation_root" for row in summary["unresolved"]), summary)
        output = {k: v for k, v in self.output.items() if k != "integration_bundles"}
        output["report"] = "조합 e\u0301 · é · 한글 · 😀\n exact original"
        raw = json.dumps(output, ensure_ascii=False, indent=3).encode("utf-8")
        _, accepted = submit_history(self, "CT-default", raw)
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
        request, rejected = submit_history(self, 'CT-bad', bad)
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
        _, accepted = submit_history(self, 'CT-good', canonical_json(self.output))
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
        # This process already matched the draft, so it does not compare those bytes again
        # (이음새-정본.md §3). A process without that memo compares them and rejects changed bytes.
        read = self.engine.store.read
        with patch.dict('do_math.repository.VERIFIED_ARTIFACTS', clear=True), \
                patch.object(self.engine.store,'read',side_effect=lambda path,head:
                             b'tampered' if path==draft['path'] else read(path,head)):
            self.assertEqual(self.engine._submission_check_summary(self.engine.head,self.engine.runtime)['status'],'incomplete')


class WaitOwnershipTests(unittest.TestCase):
    def receive(self, kind, *, creates_wait=True):
        engine = bare_engine()
        action = {'id': 'AC-one', 'role': 'intent_interpretation', 'target': 'UI-one'}
        row = {'action': deepcopy(action), 'kind': kind, 'execution_id': 'EX-one', 'reason': 'pending'}
        output = {'summary': 'Checked original'}
        engine.head = 'fixed'
        engine.instance = {'lifecycle': {'state': 'initializing'}}
        engine.runtime = {'status': 'initializing', 'history': [], 'waiting_actions': {},
            'executions': {'EX-one': {'status': 'ended', 'submission_intent': {
                'output_ref': 'out', 'extensions_ref': 'ext', 'check_ref': 'check'}}}}
        engine.store = create_autospec(ResearchRepository, instance=True)
        engine.store.git_dir = 'git-' + uuid.uuid4().hex
        engine.store.read.side_effect = lambda ref, head: json.dumps(
            {'out': output, 'ext': {}, 'check': {'issues': []}}[ref]).encode()
        def apply(*args):
            if creates_wait:
                engine.runtime['waiting_actions']['AC-one'] = deepcopy(row)
            return {'status': 'accepted', 'bundles': [], 'retry_bundle_ids': []}
        if not creates_wait:
            engine.runtime['waiting_actions']['AC-one'] = deepcopy(row)
        engine._apply_submission_bundles = create_autospec(engine._apply_submission_bundles, side_effect=apply)
        engine._remove_action = create_autospec(engine._remove_action, side_effect=lambda action: None)
        engine._record_task_receipt = create_autospec(engine._record_task_receipt, side_effect=lambda *args, **kwargs: None)
        # Sealing is covered separately; this fixture starts at a captured
        # submission so the wait ownership rule is the behavior under test.
        sealed = {'output': output, 'extensions': {}, 'check': {'issues': []}, 'output_ref': 'out'}
        with patch('do_math.engine.submission.read_sealed_submission', return_value=sealed):
            engine._receive_submission(action, {}, 'EX-one', {}, {}, Path('.'))
        return engine.runtime

    def test_new_user_wait_survives_successful_response(self):
        for kind in ('import_application_authority', 'import_user_decision'):
            with self.subTest(kind=kind):
                runtime = self.receive(kind)
                self.assertIn('AC-one', runtime['waiting_actions'])
                self.assertEqual(runtime['waiting_actions']['AC-one']['kind'], kind)

    def test_resolved_publication_and_impact_waits_are_removed(self):
        for kind in ('submission_publication', 'impact_review'):
            self.assertNotIn('AC-one', self.receive(kind, creates_wait=False)['waiting_actions'])


class ReceiptPreservationTests(unittest.TestCase):
    def test_dependency_impact_keeps_execution_and_activity_receipts_unchanged(self):
        from do_math import knowledge
        instance = {'knowledge': {'KN': {'id': 'KN', 'family': 'knowledge'}}}
        runtime = {'executions': {'EX': {'id': 'EX', 'status': 'ended', 'outcome': 'output_accepted'}},
                   'activities': {'AY': {'id': 'AY', 'status': 'finished'}}, 'queue': []}
        _, changed = knowledge._apply_impact_effects(instance, runtime, {'EX', 'AY'}, {'KN'},
                                                    reason='Source changed', impact_digest='a' * 64)
        self.assertEqual(changed['executions'], runtime['executions'])
        self.assertEqual(changed['activities'], runtime['activities'])
        self.assertEqual(changed['history'][-1]['affected_ids'], ['AY', 'EX'])

    def test_accepted_batch_opens_one_plan_and_preserves_all_evidence(self):
        for count in (3, 1, 0):
            engine = routing_engine()
            engine.instance = knowledge_io.ensure_ontology(engine.instance)
            engine.runtime['tasks']['TK'] = {'id': 'TK', 'results': [], 'status': 'active'}
            engine.runtime['executions']['EX'] = {'id': 'EX', 'role': 'research_work', 'status': 'running', 'extensions': {}}
            output = {'summary': 'Report', 'questions': [], 'used_sources': [], 'outcome': 'partial', 'report': 'Actual report',
                'remaining_work': ['Open obligation'], 'checkpoint': '', 'relations': [],
                'knowledge': [knowledge_candidate(title='K' + str(i), lean_code='', declaration_names=[]) for i in range(count)]}
            engine._apply({'id': 'AC', 'role': 'research_work', 'target': 'TK'}, output, 'EX')
            plans = [a for a in engine.runtime['queue'] if a['role'] == 'research_plan']
            self.assertEqual(len(plans), 1, plans)
            self.assertEqual(set(plans[0]['evidence_refs']), set(engine.instance['knowledge']))
            self.assertEqual(plans[0]['receipt_refs'], ['EX'])
        _, runtime, _ = knowledge_io.import_candidate({}, {}, knowledge_candidate(lean_code='', declaration_names=[]),
            source_ref='source', actor_ref='user')
        self.assertEqual([a['role'] for a in runtime['queue']], ['research_plan'])
        _, runtime, _ = knowledge_io.import_candidate({}, {}, knowledge_candidate(), source_ref='source', actor_ref='user', plan_nonformal=False)
        self.assertEqual([a['role'] for a in runtime['queue']], ['formal_check'])


class FixedResearchReferenceTests(unittest.TestCase):
    def test_fixed_sources_and_collectable_workspace_paths(self):
        self.assertIsNone(submission.fixed_research_reference_path('proposal', {'proposal'}))
        self.assertEqual(submission.fixed_research_reference_path('workspace:result.txt', {'proposal'}), 'result.txt')
        for reference in ['KN-unassigned', 'workspace:../escape', 'workspace:input/source.txt',
                          'workspace:C:/escape', 'workspace:.scratch/discarded.txt']:
            with self.subTest(reference=reference), self.assertRaises(ValueError):
                submission.fixed_research_reference_path(reference, {'proposal'})


class PartialCaptureTests(unittest.TestCase):
    def test_only_independent_local_errors_can_be_captured(self):
        from do_math import contracts
        from record_fixtures import two_observation_output, research_work_context
        from do_math.repository import canonical_json
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            visible = {**research_work_context(), 'execution_id': 'EX-partial'}
            schema = contracts.action_schema(visible['action'])
            submission.install_tools(workspace, visible, schema, None)
            output = two_observation_output()
            output['knowledge'][1]['dependencies'] = ['KN-not-supplied']
            def seal(value):
                return submission.seal_submission(workspace, execution_id='EX-partial', context=visible,
                    schema=schema, max_artifact_bytes=1024*1024, raw_output=canonical_json(value))
            sealed = seal(output)
            self.assertFalse(sealed['passed'])
            self.assertTrue(sealed['capture_eligible'], sealed['check']['issues'])
            self.assertEqual(sealed['artifacts']['output.json'], canonical_json(output))
            all_bad = deepcopy(output)
            all_bad['knowledge'][0]['dependencies'] = ['KN-not-supplied']
            self.assertFalse(seal(all_bad)['capture_eligible'])
            connected = deepcopy(output)
            connected['knowledge'][1]['dependencies'] = ['A']
            self.assertFalse(seal(connected)['capture_eligible'])
            malformed = deepcopy(output)
            malformed.pop('report')
            self.assertFalse(seal(malformed)['capture_eligible'])


class PartialCaptureGitTests(unittest.TestCase):
    def setUp(self):
        from do_math import contracts, knowledge_io, planning
        from do_math.input_basis import capture_decision_basis
        from do_math.repository import canonical_json
        from record_fixtures import two_observation_output
        start_submission_history(self)
        action = {'id': 'AC-partial', 'role': 'research_work'}
        self.engine._action_lifecycle_gate(action)
        execution = self.engine._register_execution(action, {'id': 'EX-partial', 'role': 'research_work', 'status': 'running'})
        from research_fixtures import candidate
        wire = candidate()
        wire['profile_refs'] = [execution['execution_profile_ref']]
        wire['authority_refs'] = [action['grant_id']]
        task = contracts.task_candidate_record(wire, task_id='TK-partial')
        task.pop('revises_task_id', None)
        task.update(status='planned', results=[], reviews=[], occurrence_condition={'op': 'always'})
        self.engine.runtime['tasks'][task['id']] = task
        reviewer = {'id': 'AC-review', 'role': 'task_contract_review', 'target': task['id']}
        self.engine._register_execution(reviewer, {'id': 'EX-review', 'role': 'task_contract_review', 'status': 'running'})
        approve_contract(self.engine.instance, self.engine.runtime, task)
        action['target'] = task['id']
        execution['action']['target'] = task['id']
        execution['contract_sha256'] = planning.contract_hash(task)
        self.engine._save()
        execution = self.engine.runtime['executions']['EX-partial']
        execution.update(grant_id=action['grant_id'], input_bundle='BA-partial-input', input_snapshot=self.engine.head,
            decision_basis=capture_decision_basis(self.engine.instance, self.engine.runtime, []),
            **planning.governance_revisions(self.engine.instance))
        self.workspace = Path(self.engine.instance['workspace'])/'runs/EX-partial/workspace'
        self.workspace.mkdir(parents=True)
        self.context = {'action': action, 'execution_id': 'EX-partial', 'snapshot': self.engine.head,
            'tasks': [deepcopy(task)], 'sources': [], 'knowledge_catalog': [],
            'kind_definitions': knowledge_io.catalog_definitions(self.engine.instance),
            'grants': [deepcopy(self.engine.instance['grants'][action['grant_id']])]}
        self.schema = contracts.action_schema(action)
        submission.install_tools(self.workspace, self.context, self.schema, None)
        self.engine._save({'runtime/artifacts/BA-partial-input/input/submission/context.json': canonical_json(self.context),
                           'runtime/artifacts/BA-partial-input/schema.json': canonical_json(self.schema)})
        self.binding = self.transport.issue('EX-partial', action['grant_id'], workspace=self.workspace)
        self.output = two_observation_output()
        # The independent A record can be imported without the returned report's
        # task disposition; this fixture intentionally tests the capture seam.
        self.output['integration_bundles'][0]['members'].remove('output')
        self.output['integration_bundles'][1]['members'].append('output')
        self.output['knowledge'][1]['dependencies'] = ['KN-not-supplied']

    def test_early_submission_preview_reload_and_partial_application(self):
        from do_math.repository import canonical_json
        execution = self.engine.runtime['executions']['EX-partial']
        raw = canonical_json(self.output)
        (self.workspace/'draft.json').write_bytes(raw)
        head = self.engine.head
        preview = self.engine._preview_submission(execution, {'draft_path': 'draft.json'})
        self.assertEqual(self.engine.head, head)
        self.assertEqual([row['status'] for row in preview['bundles']], ['preview_passed', 'returned'], preview)
        request = {**self.binding, 'request_id': 'CT-partial', 'kind': 'submit_intent', 'payload': {'draft_path': 'draft.json'}}
        receipt = self.transport.receive(request, publish=self.engine._publish_control_request)
        self.assertEqual(receipt['state'], 'accepted', receipt)
        self.engine = ResearchEngine(self.repo, self.identifier)
        execution = self.engine.runtime['executions']['EX-partial']
        sealed = submission.read_sealed_submission(execution, self.engine.head, self.engine.store.read)
        self.assertFalse(sealed['check']['passed'])
        self.assertEqual(self.engine._submission_check_summary(self.engine.head, self.engine.runtime)['status'], 'verified')
        applied = self.engine._apply_submission_bundles(execution['action'], sealed['output'], sealed['extensions'],
            execution['id'], self.context, sealed['check']['issues'])
        self.assertEqual([row['status'] for row in applied['bundles']], ['accepted', 'returned'], applied['issues'])
        repeated = self.engine._apply_submission_bundles(execution['action'], sealed['output'], sealed['extensions'],
            execution['id'], self.context, sealed['check']['issues'])
        self.assertEqual(repeated['bundles'][0]['status'], 'already_accepted')

    def test_native_final_reaches_the_same_partial_candidate(self):
        from do_math.repository import canonical_json
        execution = self.engine.runtime['executions']['EX-partial']
        result = native_result(execution, self.context, canonical_json(self.output), self.workspace)
        captured = self.engine._collect_submitted_result(execution, result, self.context, self.schema, self.workspace)
        self.assertEqual(captured['collection'], 'sealed_submission', captured)
        self.assertNotIn('rejected_submission', captured)
        received = self.engine._receive_submission(execution['action'], captured, execution['id'], self.context,
                                                   self.schema, self.workspace, preserved=True)
        self.assertEqual([row['status'] for row in received['bundles']], ['accepted', 'returned'], received['issues'])


class KnowledgeConnections(unittest.TestCase):
    def test_research_receipt_creates_separate_knowledge_authorities(self):
        engine = routing_engine()
        engine.instance.update(sources=[], kind_definitions={})
        engine.instance["config"]["reviewers"] = 2
        engine.runtime["tasks"]["TK-work"] = {"id": "TK-work", "status": "active", "results": []}
        engine.runtime["executions"]["EX-work"] = {"id": "EX-work", "status": "ended", "extensions": {}}
        output = {"summary": "result", "used_sources": [], "questions": [], "report": "Established a result",
                  "outcome": "submitted", "remaining_work": [], "checkpoint": "done", "relations": [],
                  "knowledge": [{"kind": "theorem", "title": "T", "statement": "True", "explanation": "By construction",
                                 "summary": "True holds", "lean_code": "theorem t : True := by trivial",
                                 "declaration_names": ["t"], "dependencies": []}]}
        engine._apply({"id": "AC-work", "role": "research_work", "target": "TK-work"}, output, "EX-work")
        record = next(iter(engine.instance["knowledge"].values()))
        self.assertNotIn("lean_code", record)
        self.assertNotIn("formal", record)
        self.assertNotIn("reviews", record)
        self.assertIn(record["formal_result_id"], engine.instance["formal_results"])
        self.assertIn(record["exposition_id"], engine.instance["expositions"])
        self.assertEqual(len(engine.runtime["tasks"]["TK-work"]["results"]), 1)
        self.assertEqual(engine.runtime["tasks"]["TK-work"]["status"], "waiting")

    def test_independent_bundle_does_not_repeat_the_task_report(self):
        engine = routing_engine()
        engine.instance.update(sources=[], kind_definitions={})
        engine.instance["config"]["reviewers"] = 2
        engine.runtime["tasks"]["TK-work"] = {"id": "TK-work", "status": "waiting", "results": [{"report": "already accepted"}]}
        engine.runtime["executions"]["EX-work"] = {"id": "EX-work", "status": "ended", "extensions": {}}
        output = {"report": "already accepted", "outcome": "submitted", "remaining_work": [],
                  "summary": "result", "questions": [], "knowledge": [], "relations": []}
        engine._apply({"id": "AC-work", "role": "research_work", "target": "TK-work"}, output, "EX-work", owns_response=False)
        self.assertEqual(engine.runtime["tasks"]["TK-work"]["results"], [{"report": "already accepted"}])


class BundleConnections(unittest.TestCase):
    def test_independent_commit_survives_later_bundle_failure_and_retry(self):
        engine = routing_engine()
        engine.head = "input-snapshot"
        engine.runtime["executions"]["EX-work"] = {"id": "EX-work", "input_snapshot": engine.head}
        engine.instance["accepted_titles"] = []
        engine.store = create_autospec(ResearchRepository, instance=True)
        published = []
        def save(head, candidate):
            published.append((deepcopy(candidate["instance"]), deepcopy(candidate["runtime"])))
            return "snapshot-" + str(len(published)), deepcopy(candidate["instance"]), deepcopy(candidate["runtime"])
        # Publication receives the candidate step's validated result.
        engine.store.save_validated.side_effect = save
        engine.store.load.side_effect = lambda head=None: (head or "snapshot-" + str(len(published)),
            deepcopy(published[-1][0]), deepcopy(published[-1][1]))
        engine._validate_bundle_current = create_autospec(engine._validate_bundle_current)
        engine._validate_bundle_candidate = create_autospec(engine._validate_bundle_candidate,
            side_effect=lambda instance, runtime, bundle, *, artifacts=None: {
                "instance": deepcopy(instance), "runtime": deepcopy(runtime)})
        def apply(action, output, execution_id, *, owns_response=True, question_source_ref=None):
            for item in output["knowledge"]:
                if item["title"] == "invalid":
                    raise ValueError("rejected candidate")
                engine.instance["accepted_titles"].append(item["title"])
            if owns_response:
                engine.runtime["history"].append({"kind": "report"})
        engine._apply = create_autospec(engine._apply, side_effect=apply)
        for name in ("_apply_model_metadata", "_apply_extensions", "_apply_revision_followup",
                     "_apply_action_resolutions", "_apply_question_resolutions", "_resolve_failed_actions",
                     "_ensure_academic_followup", "_consume_action_events", "_record_task_receipt"):
            setattr(engine, name, create_autospec(getattr(engine, name)))
        engine._defer_review_for_research = create_autospec(engine._defer_review_for_research, return_value=False)
        output = {"summary": "two independent claims", "knowledge": [{"title": "valid"}, {"title": "invalid"}],
                  "relations": [], "questions": [], "integration_bundles": [
                      {"integration_id": "IN-good", "members": ["output", "output/knowledge/0"], "impact_set": [], "authority_refs": []},
                      {"integration_id": "IN-bad", "members": ["output/knowledge/1"], "impact_set": [], "authority_refs": []}]}
        action = {"id": "AC-work", "role": "research_work", "target": "TK-work"}
        context = {"action": action, "snapshot": engine.head}
        result = engine._apply_submission_bundles(action, output, {}, "EX-work", context, [])
        self.assertEqual(result["retry_bundle_ids"], ["IN-bad"])
        self.assertEqual(engine.instance["accepted_titles"], ["valid"])
        self.assertEqual(len(published), 1)
        engine._record_task_receipt.assert_not_called()
        self.assertIn("IN-good", published[0][1]["integrations"])
        result = engine._apply_submission_bundles(action, output, {}, "EX-work", context, [])
        self.assertEqual(result["bundles"][0]["status"], "already_accepted")
        self.assertEqual(engine.instance["accepted_titles"], ["valid"])
        self.assertEqual(len(published), 1)


class CentralSubmissionEvidence(unittest.TestCase):
    def fixture(self, root):
        engine = routing_engine()
        engine.instance['config']['max_output_repairs'] = 1
        output = {"summary": "preserved exact draft"}
        raw = json.dumps(output, indent=4).encode()
        from do_math import submission, contracts
        context = {"execution_id": "EX-work", "action": {"id": "AC-work", "role": "maintenance"}, "kind_definitions": {},
                   "knowledge_catalog": [], "tasks": []}
        schema = contracts.identify_schema({"type": "object", "properties": {"summary": {"type": "string"}}, "required": ["summary"]})
        submission.install_tools(root, context, schema, 10000000)
        (root / "draft.json").write_bytes(raw)
        engine._response_schema = create_autospec(engine._response_schema, return_value=schema)
        execution = {"id": "EX-work", "action": context["action"], "status": "stopping"}
        return engine, output, context, execution

    def test_unsealed_runner_output_is_preserved_but_cannot_be_integrated(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            engine, output, context, execution = self.fixture(root)
            engine.runtime["executions"]["EX-work"] = execution
            engine._apply_submission_bundles = create_autospec(engine._apply_submission_bundles, return_value={"status": "returned", "bundles": [],
                "issues": [], "retry_bundle_ids": []})
            engine._remove_action = create_autospec(engine._remove_action)
            engine._record_task_receipt = create_autospec(engine._record_task_receipt)
            engine._save = create_autospec(engine._save)
            result = engine._receive_submission(context["action"], {"output": output}, "EX-work",
                context, engine._response_schema(context["action"]), root)
            self.assertEqual(result["status"], "returned")
            issues = engine._apply_submission_bundles.call_args.args[-1]
            self.assertTrue(any(issue["rule_id"] == "submission.sealed_candidate" for issue in issues))
            saved = engine._save.call_args.args[0]
            self.assertTrue(any(path.endswith("/output.json") for path in saved))

    def test_retry_receives_prior_accepted_response_across_multiple_attempts(self):
        engine = routing_engine()
        engine.runtime["executions"].update({"EX-one": {"action": {}},
            "EX-two": {"action": {"continuation_of": "EX-one"}}})
        receipt = {"id": "IN-report", "execution_id": "EX-one", "response_sha256": "a" * 64}
        engine.runtime["integrations"] = {receipt["id"]: receipt}
        issue = integration.issue("integration.candidate", "output", "repair this")
        context = {}
        engine._submission_repair_context(context, {"continuation_of": "EX-two", "repair": {"issues": [issue]}})
        self.assertEqual(context["accepted_response"], {"integration_id": "IN-report", "response_sha256": "a" * 64})
        self.assertEqual(context["submission_failures"], [issue])
        self.assertEqual(context["accepted_integration_ids"], ["IN-report"])


class ContinuationConnections(unittest.TestCase):

    def test_same_domain_callback_is_available_to_preview_without_publication(self):
        engine = routing_engine()
        engine.head = "snapshot"
        engine.runtime["executions"]["EX-one"] = {"id": "EX-one", "extensions": {}}
        engine._apply_model_metadata = create_autospec(engine._apply_model_metadata)
        engine._defer_review_for_research = create_autospec(engine._defer_review_for_research, return_value=False)
        engine._apply_extensions = create_autospec(engine._apply_extensions)
        engine._apply_revision_followup = create_autospec(engine._apply_revision_followup)
        engine._apply_action_resolutions = create_autospec(engine._apply_action_resolutions)
        engine._apply_question_resolutions = create_autospec(engine._apply_question_resolutions)
        engine._consume_action_events = create_autospec(engine._consume_action_events)
        engine._record_task_receipt = create_autospec(engine._record_task_receipt)
        engine._save = create_autospec(engine._save, side_effect=AssertionError("preview cannot publish"))
        engine._apply = create_autospec(engine._apply, side_effect=lambda *a, **kw: engine.runtime["history"].append({"kind": "candidate"}))
        original = deepcopy((engine.instance, engine.runtime))
        instance, runtime = deepcopy(original)
        bundle = {"integration_id": "IN-one", "output": {}, "extensions": {}, "owns_response": True}
        engine._apply_bundle_candidate(instance, runtime, bundle, action={"role": "research_work"},
                                       execution_id="EX-one", extensions={})
        self.assertEqual((engine.instance, engine.runtime), original)
        self.assertEqual(runtime["history"], [{"kind": "candidate"}])
        engine._save.assert_not_called()
        engine._record_task_receipt.assert_not_called()

    def test_bundle_live_prior_hash_and_transitive_impact_are_required(self):
        from do_math import knowledge, knowledge_io
        engine = routing_engine()
        engine.instance.update(sources=[], kind_definitions={})
        engine.instance, engine.runtime, kid = knowledge_io.import_candidate(engine.instance, engine.runtime,
            {"kind": "theorem", "title": "T", "statement": "True", "summary": "True", "explanation": "Proof",
             "lean_code": "theorem t : True := by trivial", "declaration_names": ["t"], "dependencies": []},
            source_ref="EX-author", actor_ref="EX-author")
        engine.runtime["tasks"]["TK-dependent"] = {"id": "TK-dependent", "dependencies": [kid]}
        change = {"id": kid, "changes": {"summary": "New summary"}, "reason": "clarification", "impact_set": ["TK-dependent"]}
        bundle = {"integration_id": "IN-revision", "output": {}, "owns_response": False,
                  "extensions": {"knowledge_changes": [change]}, "impact_set": ["TK-dependent"],
                  "previous_hashes": {kid: knowledge.content_hash(engine.instance["knowledge"][kid])},
                  "members": ["activity-extensions.json/knowledge_changes/0"], "payload_sha256": "a" * 64}
        engine.head = "fixed"
        action = {"id": "AC-revise", "role": "research_work"}
        engine.runtime["executions"]["EX-author"] = {"id": "EX-author", "role": "research_work", "input_snapshot": "fixed"}
        engine._validate_bundle_impacts(engine.instance, engine.runtime, bundle, action=action, execution_id="EX-author")
        changed = deepcopy(bundle); changed["impact_set"] = []
        with self.assertRaisesRegex(ValueError, "impact"):
            engine._validate_bundle_impacts(engine.instance, engine.runtime, changed, action=action, execution_id="EX-author")
        engine.instance["knowledge"][kid]["title"] = "Changed after input"
        with self.assertRaisesRegex(ValueError, "hash|changed"):
            engine._validate_bundle_impacts(engine.instance, engine.runtime, bundle, action=action, execution_id="EX-author")


class LivePreviewConnections(unittest.TestCase):
    def test_installed_preview_uses_receiver_domain_callback_without_publication(self):
        from do_math import submission, contracts
        from do_math.control_transport import ControlTransport
        import time
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "runs/EX-work/workspace"; workspace.mkdir(parents=True)
            engine = routing_engine(); engine.instance["workspace"] = str(root)
            engine.instance["config"]["max_artifact_bytes"] = 10000000
            engine.head = "fixed-snapshot"
            transport = ControlTransport(root / "transport")
            binding = transport.issue("EX-work", "GR-one")
            action = {"id": "AC-work", "role": "maintenance", "grant_id": "GR-one"}
            context = {"snapshot": engine.head, "execution_id": "EX-work", "action": action,
                "kind_definitions": {}, "knowledge_catalog": [], "tasks": [], "control_binding": binding}
            schema = contracts.with_integration_schema(contracts.schema_for("maintenance"))
            output = {"summary": "Checked draft", "used_sources": [], "questions": [], "report": "Preserved maintenance findings",
                "remaining_work": [], "integration_bundles": [{"integration_id": "IN-one", "members": ["output"], "impact_set": [], "authority_refs": []}]}
            submission.install_tools(workspace, context, schema, 10000000)
            (workspace / "draft.json").write_bytes(canonical_json(output))
            engine.runtime["executions"]["EX-work"] = {"id": "EX-work", "status": "running", "grant_id": "GR-one", "action": action, "input_bundle": "BA-input"}
            engine.store = create_autospec(ResearchRepository, instance=True)
            engine.store.read.side_effect = lambda path, head: canonical_json(schema) if path.endswith("schema.json") else (workspace / "input/submission/context.json").read_bytes()
            engine._clock_guard = create_autospec(engine._clock_guard, return_value={"usable": True, "observed_utc": "2026-09-22T00:00:00Z"})
            engine._validate_bundle_current = create_autospec(engine._validate_bundle_current); engine._validate_bundle_candidate = create_autospec(engine._validate_bundle_candidate)
            engine._defer_review_for_research = create_autospec(engine._defer_review_for_research, return_value=False)
            for name in ("_apply_model_metadata", "_apply_extensions", "_apply_revision_followup", "_apply_action_resolutions", "_apply_question_resolutions", "_consume_action_events"):
                setattr(engine, name, create_autospec(getattr(engine, name)))
            before = deepcopy((engine.instance, engine.runtime))
            process = subprocess.Popen([sys.executable, "-B", str(workspace / "input/tools/check_submission.py"),
                "--output", "draft.json", "--preview", "--wait-seconds", "20"], cwd=workspace,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                with patch("do_math.engine.governance.authorize", return_value={"allowed": True}), patch.object(engine, "_apply_bundle_candidate", wraps=engine._apply_bundle_candidate) as candidate:
                    deadline = time.monotonic() + 25
                    while process.poll() is None and time.monotonic() < deadline:
                        transport.pump(engine._publish_control_request)
                        time.sleep(.02)
                    if process.poll() is None: process.kill()
                    stdout, stderr = process.communicate()
                    self.assertEqual(process.returncode, 0, stdout + stderr)
                    self.assertEqual(candidate.call_count, 1)
            finally:
                if process.poll() is None:
                    process.kill()
                process.communicate()
            self.assertEqual((engine.instance, engine.runtime), before)
            engine.store.save_with_state.assert_not_called()
            engine.store.save_validated.assert_not_called()
            receipt = next(iter(transport._receipts.values()))
            self.assertEqual(receipt["state"], "previewed")
            self.assertTrue(receipt["result"]["passed"], receipt)
            self.assertNotIn("publication_id", receipt)


class TaskReceiptTests(unittest.TestCase):
    def test_task_receipt_occurs_once_after_the_complete_bundle_result(self):
        for owner in (None, "engine"):
            with self.subTest(owner=owner), tempfile.TemporaryDirectory() as temporary:
                workspace = Path(temporary)
                from research_fixtures import sealed_maintenance_submission
                from do_math import submission
                intent, artifacts = sealed_maintenance_submission(workspace, 'EX-work')
                prefix = intent['output_ref'].removesuffix('output.json')
                intent.update(extensions_ref=prefix+'extensions.json', check_ref=prefix+'check.json')
                engine = routing_engine()
                engine.store = create_autospec(ResearchRepository, instance=True)
                engine.store.read.side_effect = lambda path, head: artifacts[path]; engine.store.git_dir = 'git-' + uuid.uuid4().hex
                engine.head = 'fixture-snapshot'
                output = submission.load_json(artifacts[intent['output_ref']])
                context = submission.load_json((workspace/'input/submission/context.json').read_bytes())
                receipt_artifacts = [{'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
                                     for path, raw in artifacts.items()]
                execution = {'id': 'EX-work', 'action': context['action'], 'status': 'stopping',
                    'submission_intent': intent,
                    'submission_receipt': {'kind': 'submit_intent', 'state': 'accepted',
                        'execution_id': 'EX-work', 'payload': {'submission_check': {'artifacts': receipt_artifacts}}}}
                engine.runtime["executions"][execution["id"]] = execution
                action = {"id": "AC-one", "role": "maintenance"}
                engine._save = create_autospec(engine._save); engine._resolve_failed_actions = create_autospec(engine._resolve_failed_actions); engine._ensure_academic_followup = create_autospec(engine._ensure_academic_followup)
                ordered = []
                result = {"status": "accepted" if owner is None else "returned", "bundles": [{"integration_id": "IN-one", "status": "accepted" if owner is None else "returned", "next_owner": owner}], "retry_bundle_ids": [] if owner is None else ["IN-one"], "issues": []}
                def bundles(*args): ordered.append("all bundles"); return result
                engine._apply_submission_bundles = create_autospec(engine._apply_submission_bundles, side_effect=bundles)
                engine._record_task_receipt = create_autospec(engine._record_task_receipt, side_effect=lambda *a, **kw: ordered.append("task receipt"))
                engine._receive_submission(action, {"output": output}, execution["id"], context, engine._response_schema(action), workspace)
                self.assertEqual(ordered, ["all bundles", "task receipt"] if owner is None else ["all bundles"])
                self.assertEqual(execution["status"], "ended" if owner is None else "stopping")
                if owner:
                    self.assertEqual(engine.runtime["queue"], [])
                    self.assertEqual(engine.runtime["waiting_actions"][action["id"]]["next_owner"], "engine")


class SubmissionPublicationWaitTests(unittest.TestCase):
    def test_sealed_response_waits_for_a_record_change_after_a_failed_identity_check(self):
        import setup_lean
        from engine_fixtures import start_submission_history, submit_history
        from research_fixtures import fixture_setup_lean
        from do_math.trust_validation import require_active_environment
        start_submission_history(self)
        engine = self.engine
        raw = canonical_json(self.output)
        _, receipt = submit_history(self, 'CT-environment', raw)
        self.assertEqual(receipt['state'], 'accepted')
        sealed_ref = engine.runtime['executions']['EX-history']['submission_intent']['output_ref']
        environment = engine.instance['trust_environments'][engine.instance['active_trust_environment']]
        lake = Path(environment['toolchain']['executable']).with_name('lake.exe')
        original = lake.read_bytes()
        apply = engine._apply
        def gated_apply(*args, **kwargs):
            # Synthetic domain consumer; the publication gate and wait are the real ones.
            require_active_environment(engine.instance, engine.runtime, current_identity=True)
            return apply(*args, **kwargs)
        with patch.object(engine, '_apply', side_effect=gated_apply):
            lake.write_bytes(b'accidentally replaced launcher')
            engine._receive_submission(self.context['action'], {}, 'EX-history', self.context, self.schema,
                                       self.workspace, preserved=True)
            waiting = engine.runtime['waiting_actions'][self.context['action']['id']]
            self.assertEqual((waiting['kind'], waiting['next_owner']), ('submission_publication', 'engine'))
            self.assertEqual(waiting['detail']['environment_id'], environment['id'])
            lake.write_bytes(original)
            with patch.object(engine, '_receive_submission', side_effect=AssertionError('retried before a change')):
                engine._retry_submission_publications()
            # A user re-records after restoring the files; the record change releases the wait.
            record_path = Path(environment['toolchain_record']['path'])
            with fixture_setup_lean(environment['toolchain'], record_path.parent / 'smoke.lean'):
                setup_lean.rerecord(['unused'], record_path.parent, record_path.parent / 'evidence', None)
            engine._retry_submission_publications()
        self.assertNotIn(self.context['action']['id'], engine.runtime['waiting_actions'])
        self.assertEqual(engine.runtime['executions']['EX-history']['outcome'], 'output_accepted')
        self.assertEqual(engine.store.read(sealed_ref), raw)
        with patch('do_math.formal.toolchain_identity_errors', side_effect=AssertionError('status checked identity')), \
             patch('do_math.trust_inventory.observe_fingerprint', side_effect=AssertionError('status scanned files')):
            engine.status()


if __name__ == "__main__":
    unittest.main()
