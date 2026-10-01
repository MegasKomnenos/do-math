"""Submission checks (``submission``, layer 2): producer and central checks, previews, captured drafts and their
history.

Checks run the real validators over temporary workspaces. Tools are installed
with a fake clock. The central-check history that the legacy test published to
a real Git repository is published through ``GitStateStore`` on the in-process
Git fake. Where the legacy test counted schema checks by wrapping the product's
``_schema_issues``, ``ObservedCalls`` counts the calls of the unchanged function.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest

import jsonschema

from do_math import contracts, integration, submission
from do_math.canonical import canonical_json
from do_math.git_store import GitStateStore
from do_math.governance import preserve_source
from support.record_builders import research_work_context, two_observation_output
from support.role_answers import candidate, review_items
from support.fakes.clock import FakeClock
from support.fakes.git_backend import make_fake, make_repository
from support.provider_probes import ObservedCalls

REFERENCE = 'reference must identify supplied input, a record of the input snapshot or a preserved workspace file: '


def install(workspace, context, schema):
    """The submission tools of one execution, installed with a fake clock."""
    return submission.install_tools(workspace, context, schema, None, clock=FakeClock())


def setUpModule():
    """Build the support archive's digests once, so no single test pays the first installation."""
    with tempfile.TemporaryDirectory() as directory:
        install(Path(directory), research_work_context(), contracts.schema_for("research_work"))


class CheckHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.context = {"action": {"role": "maintenance", "id": "AC-1", "target": "TK-1"},
                        "execution_id": "EX-1", "snapshot": "fixed", "kind_definitions": {}}
        self.schema = contracts.schema_for("maintenance")
        install(self.workspace, self.context, self.schema)
        self.draft = self.workspace / ".scratch/draft.json"
        self.draft.parent.mkdir()
        self.good = {"summary": "Check", "used_sources": [], "questions": [], "report": "Checked", "remaining_work": [],
                     "integration_bundles": [{"integration_id": "IN-1", "members": ["output"], "impact_set": [],
                                              "authority_refs": []}]}

    def check(self, value):
        from support.entry import entry
        _entry = entry()
        self.draft.write_text(json.dumps(value), encoding="utf-8")
        return submission.producer_check(self.workspace, self.draft, clock=_entry.ports.clock)

    def test_wire_candidate_id_revision_and_profiles_match_stored_contract(self):
        wire = candidate()
        wire["profile_refs"] = [{"id": "EP-test", "revision": 1, "sha256": "a" * 64}]
        original = deepcopy(wire)
        record = contracts.task_candidate_record(wire, task_id="TK-test")
        self.assertEqual(("TK-test", 1, wire["profile_refs"]), (record["id"], record["revision"], record["profile_refs"]))
        self.assertEqual(original, wire)
        revised = contracts.task_candidate_record({**wire, "revises_task_id": "TK-test"},
                                                  task_id="TK-test", previous=record)
        self.assertEqual(2, revised["revision"])
        for field, value in (("id", "TK-forged"), ("revision", 99)):
            with self.subTest(changes={field: value}), self.assertRaisesRegex(
                    ValueError, re.escape(f"invalid task candidate: Additional properties are not allowed ('{field}' was unexpected)")):
                contracts.task_candidate_record({**wire, field: value}, task_id="TK-test")
        with self.assertRaisesRegex(ValueError, "task candidate and existing contract identities differ"):
            contracts.task_candidate_record({**wire, "revises_task_id": "TK-wrong"}, task_id="TK-test", previous=record)

    def test_producer_rechecks_preserve_order_and_resolve_real_prior_failure(self):
        """About 0.25 s, over the 0.2 s unit budget: three producer checks, each writing its record under the workspace lock."""
        bad = {k: v for k, v in self.good.items() if k != "report"}
        first, second, repaired = self.check(bad), self.check(bad), self.check(self.good)
        self.assertNotEqual(first["id"], second["id"], "Repeated invocations must not collapse into one check")
        records = submission.read_producer_checks(self.workspace, repaired["id"])
        self.assertEqual([first["id"], second["id"], repaired["id"]], [row["id"] for row in records])
        self.assertEqual([1, 2, 3], [row["producer_sequence"] for row in records])
        self.assertTrue(any(row["previous_check_id"] == second["id"] for row in repaired["repairs"]))
        summary = submission.summarize_checks(records, history_window=3)
        self.assertEqual([], summary["unresolved"])
        self.assertEqual(2, summary["rule_failure_counts"][first["issues"][0]["rule_id"]])
        evidence = summary["rule_evidence"][first["issues"][0]["rule_id"]]
        self.assertEqual([first["id"], second["id"]], [row["check_id"] for row in evidence])
        self.assertEqual("maintenance", evidence[0]["producer_role"])
        self.assertEqual(first["schema_ref"], evidence[0]["schema_ref"])

    def test_central_submission_does_not_require_optional_producer_history(self):
        from support.entry import entry
        _entry = entry()
        first = self.check({k: v for k, v in self.good.items() if k != 'report'})
        self.check(self.good)
        (self.workspace / 'checks' / (first['id'] + '.json')).unlink()
        sealed = submission.seal_submission(self.workspace, '.scratch/draft.json', execution_id='EX-1',
            context=self.context, schema=self.schema, max_artifact_bytes=1024 * 1024, clock=_entry.ports.clock)
        self.assertTrue(sealed['passed'], sealed['check']['issues'])
        self.assertEqual(sealed['check']['mode'], 'receiver')
        self.assertFalse(any(path.startswith('files/checks/') for path in sealed['artifacts']))

    def test_receiver_parse_failure_is_resolved_by_a_later_valid_receiver_check(self):
        from support.entry import entry
        _entry = entry()
        def seal():
            return submission.seal_submission(self.workspace, '.scratch/draft.json', execution_id='EX-1',
                context=self.context, schema=self.schema, max_artifact_bytes=1024 * 1024, clock=_entry.ports.clock)['check']
        self.draft.write_text('{', encoding='utf-8')
        failed = seal()
        self.draft.write_text(json.dumps(self.good), encoding='utf-8')
        passed = seal()
        self.assertEqual(['submission.parse'], [row['rule_id'] for row in failed['issues']])
        self.assertTrue(passed['passed'], passed['issues'])
        self.assertEqual(failed['check_subject'], passed['check_subject'])
        passed['repairs'] = submission._repair_links([failed], passed)
        self.assertEqual([], submission.summarize_checks([failed, passed], history_window=2)['unresolved'])

    def test_changed_failure_message_is_not_a_successful_repair(self):
        from support.entry import entry
        _entry = entry()
        first = submission.check_submission({**self.good, "report": 1}, self.schema, self.context, {}, self.workspace,
            mode="producer", execution_id="EX-1", tool_sha256="same", clock=_entry.ports.clock)
        second = submission.check_submission({**self.good, "report": False}, self.schema, self.context, {},
            self.workspace, mode="producer", execution_id="EX-1", tool_sha256="same", previous=first, clock=_entry.ports.clock)
        self.assertEqual([], second["repairs"])

    def test_different_target_does_not_resolve_a_failure(self):
        from support.entry import entry
        _entry = entry()
        first = submission.check_submission({k: v for k, v in self.good.items() if k != "report"}, self.schema,
            self.context, {}, self.workspace, mode="producer", execution_id="EX-1", tool_sha256="same", clock=_entry.ports.clock)
        other = {**self.context, "action": {**self.context["action"], "target": "TK-other"}}
        after = submission.check_submission(self.good, self.schema, other, {}, self.workspace,
            mode="producer", execution_id="EX-1", tool_sha256="same", previous=first, clock=_entry.ports.clock)
        self.assertEqual([], after["repairs"])

    def test_snapshot_summary_rejects_nonobject_central_check(self):
        raw = b'[]'
        path = 'runtime/artifacts/BA-1/submission/check.json'
        seal = {'event_seq': 1, 'capture_id': 'CT-1', 'execution_id': 'EX-1', 'state': 'rejected',
                'submission_check': {'check_ref': path, 'artifacts': [
                    {'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}]}}
        with self.assertRaisesRegex(ValueError, 'machine-check content identity differs'):
            submission.summarize_snapshot_checks([seal], snapshot='fixed',
                read_artifact=lambda path, snapshot: raw, history_window=1)

    def test_snapshot_summary_reads_real_git_central_checks_and_counts_attempts(self):
        from support.entry import entry
        _entry = entry()
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        store = GitStateStore(make_repository(Path(directory.name)), 'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV',
                              backend=make_fake(), clock=FakeClock())
        seals, head = [], None
        for number, output in enumerate(({k: v for k, v in self.good.items() if k != 'report'}, self.good), 1):
            self.draft.write_bytes(canonical_json(output))
            sealed = submission.seal_submission(self.workspace, '.scratch/draft.json', execution_id='EX-1',
                context=self.context, schema=self.schema, max_artifact_bytes=1024 * 1024, clock=_entry.ports.clock)
            prefix = f'runtime/artifacts/BA-{number}/submission/'
            artifacts = {prefix + name: raw for name, raw in sealed['artifacts'].items()}
            head = store.publish(head, {'research/fixture.json': b'{}', **artifacts}).head
            seals.append({'event_seq': number, 'capture_id': f'CT-{number}', 'execution_id': 'EX-1',
                'state': 'accepted' if sealed['passed'] else 'rejected',
                'submission_check': {'check_ref': prefix + 'check.json', 'artifacts': [
                    {'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
                    for path, raw in artifacts.items()]}})
            if number == 1:
                first_head = head

        def reader(path, snapshot):
            return store.read_bytes(snapshot, path)

        def summary(rows, snapshot, window, read=reader):
            return submission.summarize_snapshot_checks(rows, snapshot=snapshot, read_artifact=read,
                                                        history_window=window)
        old = summary(seals[:1], first_head, 1)
        current = summary(seals, head, 1)
        self.assertTrue(old['unresolved'])
        self.assertEqual(current['unresolved'], [])
        self.assertEqual(current['window_check_count'], 1)
        self.assertEqual(current['seal_count'], 2)
        zero = summary(seals[:1], first_head, 0)
        self.assertEqual(zero['window_check_count'], 0)
        self.assertEqual(zero['rule_failure_counts'], {})
        self.assertEqual(zero['unresolved'], old['unresolved'])
        self.assertEqual(old, summary(seals[:1], first_head, 1))
        for changed, message in ((list(reversed(seals)), 'central checks must follow explicit public event order'),
                                 ([seals[0], {**seals[1], 'capture_id': 'CT-1'}],
                                  'central submission request was published twice')):
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                summary(changed, head, 1)
        with self.assertRaisesRegex(ValueError, 'central check artifact hash or size differs'):
            summary(seals, head, 1, lambda path, snapshot: b'{}' if path.endswith('/output.json')
                    else reader(path, snapshot))


class SubmissionBoundaryTests(unittest.TestCase):
    def test_knowledge_change_cannot_self_confirm_its_impact(self):
        from support.entry import entry
        _entry = entry()
        output = two_observation_output()
        output["knowledge"] = []
        output["integration_bundles"] = [{"integration_id": "IN-change", "members": [
            "output", "activity-extensions.json/knowledge_changes/0"], "impact_set": [], "authority_refs": []}]
        ctx = {**research_work_context(), "execution_id": "EX-current", "knowledge_catalog": [{"id": "KN-source"}]}
        extensions = {"knowledge_changes": [{"id": "KN-source", "changes": {"statement": "Corrected"},
            "reason": "Correction", "impact_set": [], "independent_confirmation": {
                "plan_digest": "a" * 64, "decision": "approve", "review_ref": "RV-unknown",
                "reviewer_ref": "EX-current", "producer_ref": "EX-current", "affected_ids": []}}]}
        # Impact approval comes only from the designated central review execution.
        with self.assertRaisesRegex(jsonschema.ValidationError,
                                    re.escape("Additional properties are not allowed ('independent_confirmation' was unexpected)")):
            jsonschema.validate(extensions, submission.extension_schema({"role": "research_work"}))
        with tempfile.TemporaryDirectory() as directory:
            issues = submission.payload_issues(output, contracts.schema_for("research_work"), ctx, extensions,
                                               Path(directory), clock=_entry.ports.clock)
        self.assertTrue(any(row["rule_id"] == "schema.additionalProperties"
                            and row["path"].startswith("activity-extensions.json/knowledge_changes/0")
                            for row in issues), issues)

    def test_central_capture_uses_exact_current_draft_after_optional_local_check(self):
        from support.entry import entry
        _entry = entry()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            ctx = {**research_work_context(), 'execution_id': 'EX-1'}
            schema = contracts.schema_for('research_work')
            install(workspace, ctx, schema)
            draft = workspace / 'draft.json'
            draft.write_bytes(canonical_json(two_observation_output()))
            producer = submission.producer_check(workspace, draft, clock=_entry.ports.clock)
            changed = draft.read_bytes() + b' \r\n'
            draft.write_bytes(changed)
            sealed = submission.seal_submission(workspace, 'draft.json', execution_id='EX-1', context=ctx,
                schema=schema, max_artifact_bytes=1024 * 1024, clock=_entry.ports.clock)
            self.assertTrue(sealed['passed'], sealed['check']['issues'])
            self.assertEqual(sealed['artifacts']['output.json'], changed)
            self.assertNotEqual(sealed['intent']['output_sha256'], producer['output_sha256'])

    def test_central_check_uses_issued_schema_despite_local_tool_mutation(self):
        from support.entry import entry
        _entry = entry()
        for relative in ('input/submission/schema.json', 'input/tools/submission-support.zip'):
            with self.subTest(path=relative), tempfile.TemporaryDirectory() as directory:
                workspace = Path(directory)
                ctx = {**research_work_context(), 'execution_id': 'EX-1'}
                schema = contracts.schema_for('research_work')
                install(workspace, ctx, schema)
                (workspace / 'draft.json').write_bytes(canonical_json(two_observation_output()))
                (workspace / relative).write_bytes(b'broken optional local tool input')
                sealed = submission.seal_submission(workspace, 'draft.json', execution_id='EX-1',
                    context=ctx, schema=schema, max_artifact_bytes=1024 * 1024, clock=_entry.ports.clock)
                self.assertTrue(sealed['passed'], sealed['check']['issues'])
                self.assertEqual(sealed['check']['schema_ref'], contracts.schema_reference(schema))

    def test_central_rejection_preserves_malformed_draft_and_available_sidecar(self):
        from support.entry import entry
        _entry = entry()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            ctx = {**research_work_context(), 'execution_id': 'EX-1'}
            schema = contracts.schema_for('research_work')
            install(workspace, ctx, schema)
            raw, sidecar = b'{broken original output', b'{broken original sidecar'
            (workspace / 'draft.json').write_bytes(raw)
            (workspace / 'activity-extensions.json').write_bytes(sidecar)
            (workspace / 'checks').mkdir(exist_ok=True)
            (workspace / 'checks/broken.json').write_bytes(b'{broken optional local diagnostic')
            sealed = submission.seal_submission(workspace, 'draft.json', execution_id='EX-1',
                context=ctx, schema=schema, max_artifact_bytes=1024 * 1024, clock=_entry.ports.clock)
            self.assertFalse(sealed['passed'])
            self.assertEqual(sealed['artifacts']['output.json'], raw)
            self.assertEqual(sealed['artifacts']['extensions.json'], sidecar)
            self.assertEqual(sealed['check']['issues'][0]['rule_id'], 'submission.parse')

    def test_producer_check_binds_exact_schema_and_raw_output_on_parse_failure(self):
        from support.entry import entry
        _entry = entry()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            ctx = research_work_context()
            ctx["execution_id"] = "EX-1"
            schema = contracts.schema_for("research_work")
            install(workspace, ctx, schema)
            draft = workspace / "broken.json"
            draft.write_bytes(b'{broken')
            result = submission.producer_check(workspace, draft, clock=_entry.ports.clock)
            self.assertFalse(result["passed"])
            self.assertEqual(contracts.schema_reference(schema), result["schema_ref"])
            self.assertEqual(hashlib.sha256(b'{broken').hexdigest(), result["output_sha256"])
            self.assertEqual("broken.json", result["raw_output_path"])
            self.assertEqual(b'{broken', draft.read_bytes())

    def test_central_preview_does_not_disclose_private_candidate_or_exception(self):
        from support.entry import entry
        _entry = entry()
        private = {"private_reviews": {"secret-review": {"decision": "secret-judgment"}}}
        with tempfile.TemporaryDirectory() as directory:
            def reject(*args):
                raise ValueError("secret-review secret-judgment")
            result = submission.preview_submission(two_observation_output(), contracts.schema_for("research_work"),
                research_work_context(), {}, Path(directory), execution_id="EX-1", tool_sha256="same",
                instance=private, runtime={}, apply_bundle=reject,
                validate_current=lambda *a: None, validate_candidate=lambda *a: None, clock=_entry.ports.clock)
            self.assertNotIn("secret-", json.dumps(result))
            self.assertNotIn("instance", result)
            self.assertNotIn("runtime", result)
            self.assertEqual({"private_reviews": {"secret-review": {"decision": "secret-judgment"}}}, private)
            self.assertFalse(result["passed"])

    def test_ineligible_sealed_preview_has_the_same_response_skeleton_without_application(self):
        from support.entry import entry
        _entry = entry()
        check = {"id": "MC-sealed", "schema_ref": "schema-ref", "input_hashes": {"raw_output": "h"},
                 "capture_eligible": False, "issues": [{"rule_id": "submission.parse", "message": "broken"}]}

        def apply(*args):
            raise AssertionError("an ineligible capture is never applied")
        result = submission.preview_submission(None, contracts.schema_for("research_work"), research_work_context(),
            None, Path("."), execution_id="EX-1", tool_sha256="same", instance={}, runtime={}, check=check,
            apply_bundle=apply, validate_current=apply, validate_candidate=apply, clock=_entry.ports.clock)
        self.assertEqual(result, {"contract_id": submission.PREVIEW_CONTRACT_ID, "check_id": "MC-sealed",
            "schema_ref": "schema-ref", "input_hashes": {"raw_output": "h"}, "authoritative": False,
            "passed": False, "issues": check["issues"], "bundles": [],
            "not_checked": ["candidate_application", "mathematical_meaning", "Lean",
                            "future_application_currentness"]})

    def test_intent_source_coverage_is_checked_before_independent_review(self):
        from support.entry import entry
        _entry = entry()
        action = {"role": "intent_interpretation", "stage": "interpret"}
        text = "첫째 둘째"
        ctx = {**research_work_context(), "action": action, "user_request": {"id": "UC-1", "text": text},
               "original_source": preserve_source("UC-1", text, origin="user_request")}
        output = dict(summary="interpret", used_sources=[], questions=[], question_details=[],
            import_units=[dict(unit_id="IU-1", source_range={"start": 0, "end": 2}, interpretation="첫째",
                owner_kind="charter", owner_ref="context:goal", payload={}, decision_refs=[], question_refs=[])],
            integration_bundles=[dict(integration_id="IN-1", members=["output"], impact_set=[], authority_refs=[])])
        with tempfile.TemporaryDirectory() as directory:
            schema = contracts.action_schema(action)
            issues = submission.payload_issues(output, schema, ctx, {}, Path(directory), clock=_entry.ports.clock)
            self.assertTrue(any(row["rule_id"] == "intent.import_units" for row in issues), issues)
            output["import_units"][0]["source_range"]["end"] = len(text)
            self.assertEqual([], submission.payload_issues(output, schema, ctx, {}, Path(directory), clock=_entry.ports.clock))

    def test_contract_review_evidence_must_be_supplied(self):
        from support.entry import entry
        _entry = entry()
        output = dict(summary="review", used_sources=[], questions=[],
                      **review_items(["MISSING"], next_owner="research"),
                      integration_bundles=[dict(integration_id="IN-1", members=["output"], impact_set=[],
                                                authority_refs=[])])
        ctx = {**research_work_context(), "action": {"role": "task_contract_review"}}
        with tempfile.TemporaryDirectory() as directory:
            issues = submission.payload_issues(output, contracts.schema_for("task_contract_review"), ctx, {},
                                               Path(directory), clock=_entry.ports.clock)
            self.assertTrue(any(row["rule_id"] == "submission.explicit_reference" for row in issues))

    def test_machine_check_compares_checkpoint_failures_in_both_modes(self):
        from support.entry import entry
        _entry = entry()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            ctx = research_work_context()
            install(workspace, ctx, contracts.schema_for("research_work"))
            (workspace / "checkpoint.json").write_text('{}', encoding="utf-8")
            args = (two_observation_output(), contracts.schema_for("research_work"), ctx, {}, workspace)
            producer = submission.check_submission(*args, mode="producer", execution_id="EX-1", tool_sha256="same", clock=_entry.ports.clock)
            receiver = submission.check_submission(*args, mode="receiver", execution_id="EX-1", tool_sha256="same",
                                                   previous=producer, clock=_entry.ports.clock)
            self.assertFalse(producer["passed"])
            self.assertTrue(any(row["path"] == "checkpoint.json" for row in producer["issues"]))
            self.assertEqual("matched", receiver["comparison"]["status"])

    def test_check_summary_preserves_unresolved_failures_outside_window(self):
        failure = integration.issue("schema.required", "output/report", "missing", "IN-A")
        records = [dict(id="MC-old", execution_id="EX-old", tool_sha256="tool", issues=[failure], repairs=[],
                        passed=False),
                   dict(id="MC-new", execution_id="EX-new", tool_sha256="tool", issues=[], repairs=[], passed=True)]
        result = submission.summarize_checks(records, history_window=1)
        self.assertEqual(1, result["window_check_count"])
        self.assertEqual(failure["issue_id"], result["unresolved"][0]["issue_id"])

    def test_comparison_uses_fixed_context_not_unreferenced_local_input_files(self):
        from support.entry import entry
        _entry = entry()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "input").mkdir()
            path = workspace / "input" / "evidence.txt"
            path.write_text("before", encoding="utf-8")
            args = (two_observation_output(), contracts.schema_for("research_work"), research_work_context(), {},
                    workspace)
            before = submission.check_submission(*args, mode="producer", execution_id="EX-1", tool_sha256="same", clock=_entry.ports.clock)
            path.write_text("after", encoding="utf-8")
            after = submission.check_submission(*args, mode="receiver", execution_id="EX-1", tool_sha256="same",
                                                previous=before, clock=_entry.ports.clock)
            self.assertEqual("matched", after["comparison"]["status"])
            changed_context = {**args[2], "snapshot": "new-authoritative-input"}
            changed = submission.check_submission(args[0], args[1], changed_context, {}, workspace,
                mode="receiver", execution_id="EX-1", tool_sha256="same", previous=before, clock=_entry.ports.clock)
            self.assertEqual("input_changed", changed["comparison"]["status"])

    def test_same_response_can_propose_a_kind_definition(self):
        props = submission.extension_schema(research_work_context()["action"])["properties"]
        self.assertIn("kind_definitions", props)

    def test_valid_schema_bundle_is_semantically_checked_even_with_invalid_sibling(self):
        from support.entry import entry
        _entry = entry()
        output = two_observation_output()
        output["knowledge"][0]["statement"] = ""
        del output["knowledge"][1]["statement"]
        with tempfile.TemporaryDirectory() as directory:
            issues = submission.payload_issues(output, contracts.schema_for("research_work"), research_work_context(),
                                               {}, Path(directory), clock=_entry.ports.clock)
        self.assertEqual({"IN-A", "IN-B"}, {row.get("integration_id") for row in issues})

    def test_malformed_metadata_returns_its_bundle_without_losing_independent_output(self):
        from support.entry import entry
        _entry = entry()
        for value in (None, [], 1, 'invalid', {'title': []}):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                output = two_observation_output()
                output['integration_bundles'][0]['members'].append('activity-extensions.json/knowledge_metadata/0')
                extensions = {'knowledge_metadata': [value]}
                issues = submission.payload_issues(output, contracts.schema_for('research_work'),
                    research_work_context(), extensions, Path(directory), clock=_entry.ports.clock)
                self.assertTrue(issues)
                self.assertEqual({row['integration_id'] for row in issues}, {'IN-A'})
                self.assertTrue(all(row['rule_id'] == 'schema.type' for row in issues), issues)
                self.assertTrue(all(row['path'].startswith('activity-extensions.json/knowledge_metadata/0')
                                    for row in issues))
                self.assertTrue(submission.capture_eligible(output, extensions, research_work_context(), issues))

    def test_operational_review_can_request_contract_revision(self):
        schema = submission.extension_schema({"role": "operational_review"})
        self.assertIn("revision_requests", schema["properties"])

    def test_valid_bundles_pass_same_preview_checker(self):
        from support.entry import entry
        _entry = entry()
        with tempfile.TemporaryDirectory() as directory:
            issues = submission.payload_issues(two_observation_output(), contracts.schema_for("research_work"),
                                               research_work_context(), {}, Path(directory), clock=_entry.ports.clock)
        self.assertEqual([], issues)

    def test_machine_checks_compare_exact_inputs_and_preserve_skipped_checks(self):
        from support.entry import entry
        _entry = entry()
        with tempfile.TemporaryDirectory() as directory:
            args = (two_observation_output(), contracts.schema_for("research_work"), research_work_context(), {},
                    Path(directory))
            producer = submission.check_submission(*args, mode="producer", execution_id="EX-1", tool_sha256="same", clock=_entry.ports.clock)
            receiver = submission.check_submission(*args, mode="receiver", execution_id="EX-1", tool_sha256="same",
                                                   previous=producer, clock=_entry.ports.clock)
            self.assertEqual("matched", receiver["comparison"]["status"])
            forged = deepcopy(producer)
            forged["issues"] = [{"rule_id": "x", "path": "output", "issue_id": "x", "message": "x"}]
            receiver = submission.check_submission(*args, mode="receiver", execution_id="EX-1", tool_sha256="same",
                                                   previous=forged, clock=_entry.ports.clock)
            self.assertEqual("tool_defect", receiver["comparison"]["status"])
            malformed = submission.check_submission({}, contracts.schema_for("research_work"), research_work_context(),
                {}, Path(directory), mode="producer", execution_id="EX-1", tool_sha256="same", clock=_entry.ports.clock)
            self.assertIn("payload_semantics", malformed["not_checked"])
            self.assertTrue(all("issue_id" in row and "rule_id" in row for row in malformed["issues"]))

    def test_governance_and_split_evidence_are_visible_but_arbitrary_nested_ids_are_not(self):
        context = {'governance': {'charter': {'id': 'CH-adopted'},
            'policy_records': [{'id': 'PO-adopted'}], 'research_context': [{'id': 'CX-adopted'}],
            'additional_audits': [{'id': 'AA-adopted'}], 'example': {'id': 'CH-example'}},
            'knowledge_catalog': [{'id': 'KN-result', 'formal_result_id': 'FR-result',
                                   'identity_assessment_ids': ['IA-result']}],
            'goal_judgments': [{'id': 'GJ-result'}]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for identifier in ('CH-adopted', 'PO-adopted', 'CX-adopted', 'AA-adopted', 'FR-result', 'IA-result',
                               'GJ-result'):
                self.assertIsNone(submission.validate_reference(identifier, context, root))
            context['reference_catalog'] = [{'value': 'invented'}]
            for identifier in ('CH-example', 'invented', 'CH-not-delivered'):
                with self.subTest(identifier=identifier), \
                        self.assertRaisesRegex(ValueError, re.escape(REFERENCE + identifier + ';')):
                    submission.validate_reference(identifier, context, root)


class SubmissionShapeTests(unittest.TestCase):
    def fixture(self, *, explicit=True):
        context = {'action': {'role': 'maintenance'}, 'execution_id': 'EX-1',
                   'snapshot': 'fixed', 'kind_definitions': {}}
        output = {'summary': 'Inspect', 'used_sources': [], 'questions': [],
                  'report': 'Inspected', 'remaining_work': []}
        if explicit:
            output['integration_bundles'] = [{'integration_id': 'IN-1', 'members': ['output'],
                                              'impact_set': [], 'authority_refs': []}]
        return output, contracts.schema_for('maintenance'), context

    def test_unsplit_explicit_and_generated_bundles_check_shapes_once(self):
        from support.entry import entry
        _entry = entry()
        for explicit in (True, False):
            output, schema, context = self.fixture(explicit=explicit)
            original = deepcopy(output)
            with self.subTest(explicit=explicit):
                with ObservedCalls(schema=submission._schema_issues) as checks:
                    self.assertEqual(submission.payload_issues(output, schema, context, {}, Path('.'), clock=_entry.ports.clock), [])
                self.assertEqual(checks.count('schema'), 2)  # Response and extensions, once each.
                self.assertIn('integration_bundles', checks.captured('schema')[0]['value'])
                self.assertEqual(output, original)

    def test_inner_entry_still_rejects_unchecked_malformed_input(self):
        from support.entry import entry
        _entry = entry()
        output, schema, context = self.fixture()
        output.pop('report')
        inner = submission._payload_issues(output, schema, context, {}, Path('.'), clock=_entry.ports.clock)
        outer = submission.payload_issues(output, schema, context, {}, Path('.'), clock=_entry.ports.clock)
        self.assertTrue(inner)
        self.assertEqual(outer, inner)
        self.assertTrue(all(row['rule_id'].startswith('schema.') for row in inner))

    def test_early_bundle_rejection_keeps_schema_errors_first(self):
        from support.entry import entry
        _entry = entry()
        output, schema, context = self.fixture()
        output.pop('report')
        output['integration_bundles'][0]['members'] = ['unknown']
        expected = (submission._schema_issues(output, schema, 'output') +
            submission._schema_issues({}, submission.extension_schema(context['action']), 'activity-extensions.json') +
            integration.inspect_bundles(output, {}, context))
        self.assertEqual(submission.payload_issues(output, schema, context, {}, Path('.'), clock=_entry.ports.clock), expected)
        self.assertTrue(expected[0]['rule_id'].startswith('schema.'))

    def test_split_keeps_local_errors_and_checks_valid_siblings(self):
        from support.entry import entry
        _entry = entry()
        output = two_observation_output()
        output['knowledge'][0]['statement'] = ''  # Semantic defect in A.
        del output['knowledge'][1]['statement']  # Schema defect in B.
        with ObservedCalls(schema=submission._schema_issues) as checks:
            issues = submission.payload_issues(output, contracts.schema_for('research_work'), research_work_context(),
                                               {}, Path('.'), clock=_entry.ports.clock)
        self.assertEqual({row['integration_id'] for row in issues}, {'IN-A', 'IN-B'})
        self.assertEqual(checks.count('schema'), 6)  # Original and both distinct slices.

    def test_split_original_validation_is_not_replaced_by_generated_bundle(self):
        from support.entry import entry
        _entry = entry()
        output = two_observation_output()
        output.pop('integration_bundles')
        schema = contracts.schema_for('research_work')
        schema['required'].append('integration_bundles')
        supplied = {**research_work_context(), 'execution_id': 'EX-fixed'}
        issues = submission.payload_issues(output, schema, supplied, {}, Path('.'), clock=_entry.ports.clock)
        self.assertTrue(any(row['rule_id'] == 'schema.required' and
                            row['path'] == 'output/integration_bundles' for row in issues))
        self.assertNotIn('integration_bundles', output)


if __name__ == "__main__":
    unittest.main()
