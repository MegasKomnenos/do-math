"""Central capture and sealed reading (``submission``, ``execution_lifecycle``, ``knowledge``; layer 2).

The centrally sealed submission flow, seen from its layer-2 functions: the
central seal fixes the exact bytes it checked, the issued input is parsed once
per content, a sealed candidate is read back from its receipt only when every
binding matches, and a partial candidate is capturable only when its failures
are independent. Tools are installed with a fake clock; the receipt test
publishes through ``GitStateStore`` on the in-process Git fake. Where the
legacy tests replaced a product name to count or race a call, the probes
observe the unchanged product (``ObservedCalls``, ``CallSites``).
"""
from copy import deepcopy
import hashlib
from pathlib import Path
import re
import tempfile
import unittest
import uuid

from do_math import contracts, execution_lifecycle, knowledge, knowledge_io, repository, submission
from do_math.canonical import canonical_json, exact_content_hash
from do_math.context_store import collect_outputs
from do_math.control_transport import ControlTransport
from do_math.git_store import GitStateStore
from support.knowledge_builders import knowledge_candidate
from support.record_builders import research_work_context, two_observation_output
from support.role_answers import seal_response
from support.fakes.clock import FakeClock
from support.fakes.git_backend import make_fake, make_repository
from support.provider_probes import ObservedCalls
from support.submission_probes import CallSites

UNBOUND = 'sealed check does not bind this candidate'


def setUpModule():
    """Build the support archive's digests once, so no single test pays the first installation."""
    with tempfile.TemporaryDirectory() as directory:
        submission.install_tools(Path(directory), research_work_context(), contracts.schema_for("research_work"),
                                 None, clock=FakeClock())


def receipt_for(artifacts):
    """An accepted submission receipt whose artifact rows name ``artifacts`` (path: bytes)."""
    return {'state': 'accepted', 'execution_id': 'EX-flow', 'payload': {'submission_check': {
        'artifacts': [{'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
                      for path, raw in artifacts.items()]}}}


class SealedCaptureTests(unittest.TestCase):
    """The legacy ``SubmissionFlowTests`` scene: a maintenance execution's workspace with installed tools."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.clock = FakeClock()
        self.workspace = Path(self.temporary.name) / "workspace"
        self.workspace.mkdir()
        self.transport = ControlTransport(Path(self.temporary.name) / "delivery", clock=self.clock)
        self.binding = self.transport.issue("EX-flow", "GR-flow", workspace=self.workspace)
        self.context = {"action": {"role": "maintenance", "id": "AC-flow"}, "execution_id": "EX-flow",
                        "control_binding": self.binding, "snapshot": "fixed", "tasks": [], "knowledge_catalog": [],
                        "sources": [], "kind_definitions": {}}
        self.schema = contracts.schema_for("maintenance")
        submission.install_tools(self.workspace, self.context, self.schema, None, clock=self.clock)
        self.output = {"summary": "Inspect only", "used_sources": [], "questions": [], "report": "Inspected",
                       "remaining_work": []}
        seal_response(self.output, self.context, self.workspace)
        self.draft = self.workspace / ".scratch" / "draft.json"
        self.draft.parent.mkdir()
        self.draft.write_bytes(canonical_json(self.output))

    def seal(self, draft=".scratch/draft.json"):
        return submission.seal_submission(self.workspace, draft, execution_id="EX-flow", context=self.context,
                                          schema=self.schema, max_artifact_bytes=1024 * 1024, clock=self.clock)

    def test_central_candidate_is_read_from_its_git_receipt_without_legacy_fields(self):
        sealed = self.seal()
        self.assertTrue(sealed['passed'], sealed['check']['issues'])
        prefix = 'runtime/artifacts/BA-central/submission'
        artifacts = {prefix + '/' + path: raw for path, raw in sealed['artifacts'].items()}
        intent = {**sealed['intent'], 'output_ref': prefix + '/output.json',
                  'extensions_ref': prefix + '/extensions.json', 'check_ref': prefix + '/check.json'}
        receipt = receipt_for(artifacts)
        execution = {'id': 'EX-flow', 'submission_intent': intent, 'submission_receipt': receipt}
        store = GitStateStore(make_repository(Path(self.temporary.name) / 'repo'), 'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV',
                              backend=make_fake(), clock=self.clock)
        head = store.publish(None, {'research/fixture.json': b'{}', **artifacts}).head

        def read(path, snapshot):
            return store.read_bytes(snapshot, path)
        recovered = submission.read_sealed_submission(execution, head, read)
        self.assertEqual(recovered['output'], self.output)
        self.assertEqual(recovered['extensions'], {})
        # With the repository identity, a sealed row is hashed once per process (이음새-정본.md §3).
        with CallSites(hashlib.sha256) as matching:
            self.assertEqual(submission.read_sealed_submission(execution, head, read, git_dir=store.git_dir),
                             recovered)
        # The first read with the identity matches each of the three sealed rows once (the probe sees them).
        self.assertEqual(3, matching.count(repository))
        with CallSites(hashlib.sha256) as hashing:
            self.assertEqual(submission.read_sealed_submission(execution, head, read, git_dir=store.git_dir),
                             recovered)
        # The legacy test replaced submission's hashlib: the reader never hashes a row itself.
        self.assertEqual(0, hashing.count(submission))
        # The rows this process matched are not hashed again by the repository's sealed-row check either.
        self.assertEqual(0, hashing.count(repository))
        self.assertTrue(recovered['check']['passed'])

        for mutation in ('output', 'extensions', 'execution', 'mode', 'schema'):
            with self.subTest(mutation=mutation):
                changed = dict(artifacts)
                changed_intent = deepcopy(intent)
                changed_check = deepcopy(sealed['check'])
                if mutation == 'output':
                    changed[intent['output_ref']] = canonical_json({**self.output,
                                                                    'report': 'A different, unchecked report'})
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
                    changed_intent[field + '_sha256'] = hashlib.sha256(changed[intent[field + '_ref']]).hexdigest()
                with self.assertRaisesRegex(submission.SealedSubmissionError, re.escape('EX-flow: ' + UNBOUND)):
                    submission.read_sealed_submission(
                        {'id': 'EX-flow', 'submission_intent': changed_intent,
                         'submission_receipt': receipt_for(changed)},
                        head, lambda path, snapshot: changed[path])

    def test_central_seal_uses_actual_bytes_and_survives_original_draft_change(self):
        sealed = self.seal()
        self.assertTrue(sealed["passed"], sealed["check"]["issues"])
        original = self.draft.read_bytes()
        self.draft.write_bytes(canonical_json({"changed": True}))
        self.assertEqual(original, sealed["artifacts"]["output.json"])
        self.assertEqual(self.output, submission.load_json(sealed["artifacts"]["output.json"]))
        self.assertNotIn(".control/stop-request.json", {row["path"] for row in sealed["manifest"]})

    def test_central_capture_never_mixes_checked_draft_with_a_later_file_version(self):
        draft = self.workspace / "draft.json"
        original = canonical_json(self.output)
        draft.write_bytes(original)
        changed = deepcopy(self.output)
        changed["report"] = "The draft changed during central capture."

        def race(arguments):
            # Another writer replaces the draft as the output collector starts.
            draft.write_bytes(canonical_json(changed))
            return dict(arguments)
        with ObservedCalls(collect=collect_outputs, capture={'collect': race}) as calls:
            sealed = self.seal("draft.json")
        self.assertTrue(sealed["passed"], sealed["check"]["issues"])
        self.assertEqual(1, calls.count('collect'))
        self.assertEqual(sealed["artifacts"]["output.json"], sealed["artifacts"]["files/draft.json"])
        self.assertEqual(original, sealed["artifacts"]["output.json"])

    def test_control_changes_do_not_change_candidate_hashes_or_output_manifest(self):
        """About 0.2 s, at the 0.2 s unit budget: two producer checks (each writes its record) and two output collections."""
        first = submission.producer_check(self.workspace, self.draft, clock=self.clock)
        before = collect_outputs(self.workspace, max_bytes=1024 * 1024)["manifest"]
        control = self.workspace / ".control"
        control.mkdir()
        (control / "stop-request.json").write_bytes(canonical_json({"reason": "submission_intent"}))
        second = submission.producer_check(self.workspace, self.draft, clock=self.clock)
        after = collect_outputs(self.workspace, max_bytes=1024 * 1024)["manifest"]
        self.assertEqual(first["input_hashes"], second["input_hashes"])
        self.assertEqual(before, after)

    def test_illegal_draft_reference_is_rejected_before_transport(self):
        outside = self.workspace.parent / "outside.json"
        outside.write_bytes(canonical_json(self.output))
        sealed = self.seal("../outside.json")
        self.assertFalse(sealed["passed"])
        self.assertTrue(any(row["rule_id"] == "submission.read" for row in sealed["check"]["issues"]))

    def test_central_candidate_rejects_missing_workspace_reference(self):
        output = {**self.output, "used_sources": ["workspace:missing-evidence.txt"]}
        seal_response(output, self.context, self.workspace)
        self.draft.write_bytes(canonical_json(output))
        sealed = self.seal()
        self.assertFalse(sealed["passed"])
        self.assertTrue(any(row["path"] == "output/used_sources/0" and "preserved workspace file" in row["message"]
                            for row in sealed["check"]["issues"]), sealed["check"]["issues"])

    def test_empty_known_extension_is_normalized_at_capture_and_sealed_read(self):
        """About 0.25 s, over the 0.2 s unit budget: one producer check and four central seals of the workspace."""
        raw = b'{ "knowledge_changes": [] }\r\n'
        (self.workspace / "activity-extensions.json").write_bytes(raw)
        producer = submission.producer_check(self.workspace, self.draft, clock=self.clock)
        self.assertTrue(producer["passed"], producer["issues"])
        sealed = self.seal()
        self.assertTrue(sealed["passed"], sealed["check"]["issues"])
        self.assertEqual(producer["input_hashes"], sealed["check"]["input_hashes"])
        self.assertEqual(sealed["artifacts"]["extensions.json"], raw)
        self.assertEqual(sealed["artifacts"]["files/activity-extensions.json"], raw)
        prefix = "runtime/artifacts/BA-empty/"
        artifacts = {prefix + name: data for name, data in sealed["artifacts"].items()}
        intent = {**sealed["intent"], "output_ref": prefix + "output.json",
                  "extensions_ref": prefix + "extensions.json", "check_ref": prefix + "check.json"}
        recovered = submission.read_sealed_submission(
            {"id": "EX-flow", "submission_intent": intent, "submission_receipt": receipt_for(artifacts)},
            "fixed", lambda path, snapshot: artifacts[path])
        self.assertEqual(recovered["extensions"], {})
        for invalid in ({"unknown_family": []}, {"knowledge_changes": {}},
                        {"knowledge_changes": [{"id": "KN-unavailable"}]}):
            with self.subTest(invalid=invalid):
                (self.workspace / "activity-extensions.json").write_bytes(canonical_json(invalid))
                rejected = self.seal()
                self.assertFalse(rejected["capture_eligible"])

    def test_central_candidate_rejects_malformed_draft_bytes(self):
        self.draft.write_bytes(b'{"summary":')
        sealed = self.seal()
        self.assertFalse(sealed["passed"])
        self.assertTrue(any(row["rule_id"] == "submission.parse" for row in sealed["check"]["issues"]))


class IssuedInputTests(unittest.TestCase):
    def test_issued_input_is_parsed_once_per_content_and_returned_as_copies(self):
        reads = []
        # A nonce keeps these bytes apart from memo entries other tests left in the process.
        nonce = uuid.uuid4().hex

        def read(path, snapshot):
            reads.append(path)
            # Every bundle holds the same bytes for the same file name.
            return canonical_json({'file': path.rsplit('/', 1)[-1], 'nonce': nonce})
        execution = {'input_bundle': 'BA-' + uuid.uuid4().hex}
        with ObservedCalls(parse=submission.load_json) as parse:
            first, _ = submission.issued_input(execution, 'head', read)
            first['changed'] = True
            second, schema = submission.issued_input(execution, 'head', read)
            # The bytes are read on every call; each content is parsed once.
            self.assertEqual(reads, ['runtime/artifacts/' + execution['input_bundle'] + '/' + name
                                     for name in ('input/submission/context.json', 'schema.json')] * 2)
            self.assertEqual(parse.count('parse'), 2)
            self.assertNotIn('changed', second)
            self.assertEqual(schema['file'], 'schema.json')
            schema['changed'] = True
            # The same bytes under another bundle and snapshot reuse the parse, as copies.
            other, other_schema = submission.issued_input({'input_bundle': 'BA-' + uuid.uuid4().hex}, 'other', read)
            self.assertEqual(parse.count('parse'), 2)
            self.assertEqual(other, second)
            self.assertNotIn('changed', other_schema)
            # Different bytes are parsed again.
            nonce = uuid.uuid4().hex
            third, _ = submission.issued_input(execution, 'head', read)
            self.assertEqual(parse.count('parse'), 4)
            self.assertEqual(third['nonce'], nonce)


class LifecycleIntentTests(unittest.TestCase):
    def test_lifecycle_accepts_only_central_sealed_candidate_not_worker_manifest(self):
        """The name also says a worker manifest is refused; the legacy test and this one check the acceptance."""
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


class ReceiptPreservationTests(unittest.TestCase):
    def test_dependency_impact_keeps_execution_and_activity_receipts_unchanged(self):
        instance = {'knowledge': {'KN': {'id': 'KN', 'family': 'knowledge'}}}
        runtime = {'executions': {'EX': {'id': 'EX', 'status': 'ended', 'outcome': 'output_accepted'}},
                   'activities': {'AY': {'id': 'AY', 'status': 'finished'}}, 'queue': []}
        _, changed = knowledge._apply_impact_effects(instance, runtime, {'EX', 'AY'}, {'KN'},
                                                    reason='Source changed', impact_digest='a' * 64,
                                                    clock=FakeClock())
        self.assertEqual(changed['executions'], runtime['executions'])
        self.assertEqual(changed['activities'], runtime['activities'])
        self.assertEqual(changed['history'][-1]['affected_ids'], ['AY', 'EX'])

    def test_direct_imports_open_a_plan_for_nonformal_and_a_formal_check_otherwise(self):
        """The legacy ``test_accepted_batch_opens_one_plan_and_preserves_all_evidence`` ends with these imports."""
        clock = FakeClock()
        _, runtime, _ = knowledge_io.import_candidate({}, {}, knowledge_candidate(lean_code='', declaration_names=[]),
            source_ref='source', actor_ref='user', clock=clock)
        self.assertEqual([a['role'] for a in runtime['queue']], ['research_plan'])
        _, runtime, _ = knowledge_io.import_candidate({}, {}, knowledge_candidate(), source_ref='source',
                                                      actor_ref='user', plan_nonformal=False, clock=clock)
        self.assertEqual([a['role'] for a in runtime['queue']], ['formal_check'])


class FixedResearchReferenceTests(unittest.TestCase):
    def test_fixed_sources_and_collectable_workspace_paths(self):
        self.assertIsNone(submission.fixed_research_reference_path('proposal', {'proposal'}))
        self.assertEqual(submission.fixed_research_reference_path('workspace:result.txt', {'proposal'}), 'result.txt')
        for reference, message in [
                ('KN-unassigned', 'investigation evidence is outside its fixed source set'),
                ('workspace:../escape', 'unsafe relative path: ../escape'),
                ('workspace:input/source.txt', 'evidence must be a collectable workspace file: input/source.txt'),
                ('workspace:C:/escape', 'path must be a nonempty relative POSIX path'),
                ('workspace:.scratch/discarded.txt',
                 'evidence must be a collectable workspace file: .scratch/discarded.txt')]:
            with self.subTest(reference=reference), self.assertRaisesRegex(ValueError, '^' + re.escape(message) + '$'):
                submission.fixed_research_reference_path(reference, {'proposal'})


class PartialCaptureTests(unittest.TestCase):
    def test_only_independent_local_errors_can_be_captured(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            clock = FakeClock()
            visible = {**research_work_context(), 'execution_id': 'EX-partial'}
            schema = contracts.action_schema(visible['action'])
            submission.install_tools(workspace, visible, schema, None, clock=clock)
            output = two_observation_output()
            output['knowledge'][1]['dependencies'] = ['KN-not-supplied']

            def seal(value):
                return submission.seal_submission(workspace, execution_id='EX-partial', context=visible,
                    schema=schema, max_artifact_bytes=1024 * 1024, raw_output=canonical_json(value), clock=clock)
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


if __name__ == "__main__":
    unittest.main()
