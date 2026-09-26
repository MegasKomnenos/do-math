"""Feature 5 submission boundaries; real validators, isolated in-memory state."""
from copy import deepcopy
import importlib
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.repository import exact_content_hash
from do_math import contracts, submission
from do_math.repository import canonical_json


def response():
    return dict(summary="two observations", used_sources=[], questions=[], outcome="submitted",
                report="independent observations", knowledge=[knowledge("A"), knowledge("B")],
                relations=[], remaining_work=[], checkpoint="", integration_bundles=[
                    dict(integration_id="IN-A", members=["output", "output/knowledge/0"], impact_set=[], authority_refs=[]),
                    dict(integration_id="IN-B", members=["output/knowledge/1"], impact_set=[], authority_refs=[])])


def knowledge(title):
    return dict(kind="observation", title=title, statement=title, explanation=title,
                summary=title, lean_code="", declaration_names=[], dependencies=[])


def context():
    return dict(action=dict(role="research_work", target="TK-1"), snapshot="fixed",
                kind_definitions={"knowledge": [{"token": "observation"}], "relations": []},
                knowledge_catalog=[], tasks=[], sources=[], grants=[])


class AuditRepairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.context = {"action": {"role": "maintenance", "id": "AC-1", "target": "TK-1"},
                        "execution_id": "EX-1", "snapshot": "fixed", "kind_definitions": {}}
        self.schema = contracts.schema_for("maintenance")
        submission.install_tools(self.workspace, self.context, self.schema, None)
        self.draft = self.workspace / ".scratch/draft.json"
        self.draft.parent.mkdir()
        self.good = {"summary": "Check", "used_sources": [], "questions": [], "report": "Checked", "remaining_work": [],
                     "integration_bundles": [{"integration_id": "IN-1", "members": ["output"], "impact_set": [], "authority_refs": []}]}

    def check(self, value):
        self.draft.write_text(json.dumps(value), encoding="utf-8")
        return submission.producer_check(self.workspace, self.draft)

    def test_wire_candidate_id_revision_and_profiles_match_stored_contract(self):
        from research_fixtures import candidate
        wire = candidate()
        wire["profile_refs"] = [{"id": "EP-test", "revision": 1, "sha256": "a" * 64}]
        original = deepcopy(wire)
        record = contracts.task_candidate_record(wire, task_id="TK-test")
        self.assertEqual(("TK-test", 1, wire["profile_refs"]), (record["id"], record["revision"], record["profile_refs"]))
        self.assertEqual(original, wire)
        revised = contracts.task_candidate_record({**wire, "revises_task_id": "TK-test"},
                                                  task_id="TK-test", previous=record)
        self.assertEqual(2, revised["revision"])
        for changes in ({"id": "TK-forged"}, {"revision": 99}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                contracts.task_candidate_record({**wire, **changes}, task_id="TK-test")
        with self.assertRaises(ValueError):
            contracts.task_candidate_record({**wire, "revises_task_id": "TK-wrong"}, task_id="TK-test", previous=record)

    def test_installed_checker_uses_latest_schema_bytes_and_prior_check(self):
        import subprocess, zipfile
        from do_math.repository import canonical_json
        self.assertEqual(canonical_json(self.schema), (self.workspace / "input/submission/schema.json").read_bytes())
        with zipfile.ZipFile(self.workspace / "input/tools/submission-support.zip") as archive:
            for name in ("contracts.py", "submission.py", "task_contracts.py"):
                self.assertEqual((Path(submission.__file__).parent / name).read_bytes(), archive.read("do_math/" + name))
        records = []
        for value in ({k: v for k, v in self.good.items() if k != "report"}, self.good):
            self.draft.write_text(json.dumps(value), encoding="utf-8")
            process = subprocess.run([*self.context["submission_contract"]["command"], "--output", str(self.draft)],
                cwd=self.workspace, text=True, capture_output=True, encoding="utf-8", timeout=30)
            records.append(json.loads(process.stdout))
        self.assertEqual(records[0]["id"], records[1]["previous_producer_check_id"])
        self.assertTrue(records[1]["passed"])
        self.assertTrue(records[1]["repairs"])

    def test_producer_rechecks_preserve_order_and_resolve_real_prior_failure(self):
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
        first = self.check({k:v for k,v in self.good.items() if k != 'report'})
        self.check(self.good)
        (self.workspace/'checks'/(first['id']+'.json')).unlink()
        sealed = submission.seal_submission(self.workspace,'.scratch/draft.json',execution_id='EX-1',
            context=self.context,schema=self.schema,max_artifact_bytes=1024*1024)
        self.assertTrue(sealed['passed'],sealed['check']['issues'])
        self.assertEqual(sealed['check']['mode'],'receiver')
        self.assertFalse(any(path.startswith('files/checks/') for path in sealed['artifacts']))

    def test_receiver_parse_failure_is_resolved_by_a_later_valid_receiver_check(self):
        seal = lambda: submission.seal_submission(self.workspace, '.scratch/draft.json', execution_id='EX-1',
            context=self.context, schema=self.schema, max_artifact_bytes=1024*1024)['check']
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
        first = submission.check_submission({**self.good, "report": 1}, self.schema, self.context, {}, self.workspace,
            mode="producer", execution_id="EX-1", tool_sha256="same")
        second = submission.check_submission({**self.good, "report": False}, self.schema, self.context, {}, self.workspace,
            mode="producer", execution_id="EX-1", tool_sha256="same", previous=first)
        self.assertEqual([], second["repairs"])

    def test_different_target_does_not_resolve_a_failure(self):
        first = submission.check_submission({k: v for k, v in self.good.items() if k != "report"}, self.schema,
            self.context, {}, self.workspace, mode="producer", execution_id="EX-1", tool_sha256="same")
        other = {**self.context, "action": {**self.context["action"], "target": "TK-other"}}
        after = submission.check_submission(self.good, self.schema, other, {}, self.workspace,
            mode="producer", execution_id="EX-1", tool_sha256="same", previous=first)
        self.assertEqual([], after["repairs"])

    def test_snapshot_summary_rejects_nonobject_central_check(self):
        raw=b'[]'; path='runtime/artifacts/BA-1/submission/check.json'
        seal={'event_seq':1,'capture_id':'CT-1','execution_id':'EX-1','state':'rejected',
              'submission_check':{'check_ref':path,'artifacts':[{'path':path,
                  'sha256':__import__('hashlib').sha256(raw).hexdigest(),'bytes':len(raw)}]}}
        with self.assertRaises(ValueError):
            submission.summarize_snapshot_checks([seal],snapshot='fixed',
                read_artifact=lambda snapshot,path:raw,history_window=1)

    def test_snapshot_summary_reads_real_git_central_checks_and_counts_attempts(self):
        import subprocess, hashlib
        from do_math.git_store import GitStateStore
        git_directory=tempfile.TemporaryDirectory();self.addCleanup(git_directory.cleanup)
        root=Path(git_directory.name)
        subprocess.run(['git','-C',str(root),'init','-q'],check=True)
        store=GitStateStore(root,'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV')
        seals=[];head=None
        for number,output in enumerate(({k:v for k,v in self.good.items() if k!='report'},self.good),1):
            self.draft.write_bytes(canonical_json(output))
            sealed=submission.seal_submission(self.workspace,'.scratch/draft.json',execution_id='EX-1',
                context=self.context,schema=self.schema,max_artifact_bytes=1024*1024)
            prefix=f'runtime/artifacts/BA-{number}/submission/'
            artifacts={prefix+name:raw for name,raw in sealed['artifacts'].items()}
            head=store.publish(head,{'research/fixture.json':b'{}',**artifacts}).head
            seals.append({'event_seq':number,'capture_id':f'CT-{number}','execution_id':'EX-1',
                'state':'accepted' if sealed['passed'] else 'rejected',
                'submission_check':{'check_ref':prefix+'check.json','artifacts':[
                    {'path':path,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
                    for path,raw in artifacts.items()]}})
            if number==1:first_head=head
        reader=lambda snapshot,path:store.read_bytes(snapshot,path)
        old=submission.summarize_snapshot_checks(seals[:1],snapshot=first_head,read_artifact=reader,history_window=1)
        current=submission.summarize_snapshot_checks(seals,snapshot=head,read_artifact=reader,history_window=1)
        self.assertTrue(old['unresolved']);self.assertEqual(current['unresolved'],[])
        self.assertEqual(current['window_check_count'],1);self.assertEqual(current['seal_count'],2)
        zero=submission.summarize_snapshot_checks(seals[:1],snapshot=first_head,read_artifact=reader,history_window=0)
        self.assertEqual(zero['window_check_count'],0);self.assertEqual(zero['rule_failure_counts'],{})
        self.assertEqual(zero['unresolved'],old['unresolved'])
        self.assertEqual(old,submission.summarize_snapshot_checks(seals[:1],snapshot=first_head,read_artifact=reader,history_window=1))
        for changed in (list(reversed(seals)),[seals[0],{**seals[1],'capture_id':'CT-1'}]):
            with self.assertRaises(ValueError):
                submission.summarize_snapshot_checks(changed,snapshot=head,read_artifact=reader,history_window=1)
        with self.assertRaises(ValueError):
            submission.summarize_snapshot_checks(seals,snapshot=head,
                read_artifact=lambda snapshot,path:b'{}' if path.endswith('/output.json') else reader(snapshot,path),history_window=1)

class ImpactReviewTests(unittest.TestCase):
    def seal_review_fixture(self, execution, output, fixed, workspace):
        """Use the actual central capture format before testing its consumer."""
        from types import SimpleNamespace
        from do_math.engine import ResearchEngine
        from do_math.execution_lifecycle import transition_execution
        from do_math.repository import canonical_json, new_id
        schema = contracts.action_schema(fixed['action'])
        submission.install_tools(workspace, fixed, schema, None)
        (workspace / 'draft.json').write_bytes(canonical_json(output))
        sealed = submission.seal_submission(workspace, 'draft.json', execution_id=execution['id'],
            context=fixed, schema=schema, max_artifact_bytes=1024 * 1024)
        self.assertTrue(sealed['passed'], sealed['check']['issues'])
        host = SimpleNamespace(_lifecycle_event=lambda *args, **kwargs: None)
        artifacts = ResearchEngine._stage_submission_capture(host, execution, sealed,
            {'id': new_id('CT'), 'kind': 'submit_intent', 'state': 'accepted', 'execution_id': execution['id'],
             'received_at': '2026-09-20T00:00:01Z'}, origin='explicit_tool')
        transition_execution(execution, 'ended', at='2026-09-20T00:00:02Z', outcome='output_accepted')
        execution['submitted_output_ref'] = execution['submission_intent']['output_ref']
        return artifacts

    def setUp(self):
        from do_math import integration, knowledge_io
        self.api = integration
        self.instance = knowledge_io.ensure_ontology({"feature_version": 5, "knowledge": {}, "expositions": {}})
        self.runtime = {"feature_version": 5, "executions": {
            "EX-producer": {"id": "EX-producer", "role": "research_work", "status": "running", "input_snapshot": "fixed-input"}}, "queue": []}
        self.ids = []
        for title in ("A", "B", "C"):
            self.instance, self.runtime, kid = knowledge_io.import_candidate(self.instance, self.runtime,
                knowledge(title), source_ref="EX-producer", actor_ref="EX-producer")
            self.ids.append(kid)
        self.output = response()
        self.output["knowledge"] = []
        from do_math.knowledge import content_hash
        self.output["integration_bundles"] = [{"integration_id": "IN-held", "members": ["output",
            "activity-extensions.json/knowledge_changes/0", "activity-extensions.json/knowledge_changes/1"],
            "impact_set": [self.ids[1]], "authority_refs": [],
            "previous_hashes": {kid: content_hash(self.instance["knowledge"][kid]) for kid in (self.ids[0], self.ids[2])}}]
        self.extensions = {"knowledge_changes": [{"id": kid, "changes": {"summary": "Revised " + str(n)},
            "reason": "Correct explanation", "impact_set": [self.ids[1]]} for n, kid in enumerate((self.ids[0], self.ids[2]))]}
        self.bundle = next(self.api.split_bundles(self.output, self.extensions, context()))

    def request(self):
        return self.api.bundle_impact_request(self.instance, self.runtime, self.bundle,
            producer_execution_id="EX-producer", input_snapshot=self.runtime["executions"]["EX-producer"]["input_snapshot"])

    def test_request_cannot_relabel_the_original_producer_snapshot(self):
        with self.assertRaises(ValueError):
            self.api.bundle_impact_request(self.instance, self.runtime, self.bundle,
                producer_execution_id="EX-producer", input_snapshot="other-input")

    def review_output(self, request):
        return {"summary": "Independent impact assessment", "questions": [], "used_sources": [],
            "report": "Compared each declared scope with its computed dependencies and supplied premises.", "remaining_work": [],
            "impact_review": {key: deepcopy(request[key]) for key in
                ("integration_id", "payload_sha256", "producer_execution_id", "input_snapshot")} | {
                "plan_decisions": [{"scope": scope, "plan_digest": plan["digest"], "decision": "approve",
                    "affected_ids": sorted(set(plan["computed_impact"]) | set(plan["declared_impact"])),
                    "reason": "The declared additional scope must also be reassessed."} for scope, plan in request["plans"].items()]},
            "integration_bundles": [{"integration_id": "IN-review", "members": ["output"],
                                     "impact_set": [], "authority_refs": []}]}

    def test_designated_review_has_producible_closed_schema_and_exact_scope(self):
        import jsonschema
        request = self.request()
        action = {"role": "maintenance", "stage": "impact_review", "input_basis": {"impact_review": request}}
        output = self.review_output(request)
        schema = contracts.action_schema(action)
        self.assertEqual([], list(jsonschema.Draft202012Validator(schema).iter_errors(output)))
        self.api.validate_impact_review_response(request, output)
        self.assertEqual(3, len(request["plans"]))
        self.assertNotEqual(request["plans"]["bundle"]["digest"],
                            request["plans"]["activity-extensions.json/knowledge_changes/0"]["digest"])
        altered = deepcopy(output)
        altered["impact_review"]["plan_decisions"].pop()
        with self.assertRaises(ValueError):
            self.api.validate_impact_review_response(request, altered)
        altered = deepcopy(output)
        altered["impact_review"]["plan_decisions"][1]["plan_digest"] = request["plans"]["bundle"]["digest"]
        with self.assertRaises(ValueError):
            self.api.validate_impact_review_response(request, altered)
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            ctx = {"action": action, "execution_id": "EX-review", "snapshot": "review-input", "kind_definitions": {}}
            submission.install_tools(workspace, ctx, schema, None)
            draft = workspace / ".scratch/draft.json"
            draft.parent.mkdir()
            draft.write_text(json.dumps(output), encoding="utf-8")
            self.assertTrue(submission.producer_check(workspace, draft)["passed"])
            bad = deepcopy(output)
            bad["impact_review"]["plan_decisions"] = [bad["impact_review"]["plan_decisions"][0]] * 3
            draft.write_text(json.dumps(bad), encoding="utf-8")
            self.assertFalse(submission.producer_check(workspace, draft)["passed"],
                             "Installed producer must reject duplicate scope judgments")

    def test_review_required_is_a_waiting_disposition_not_a_producer_retry(self):
        result = self.api.apply_bundles(self.instance, self.runtime, self.output, self.extensions, context(),
            execution_id="EX-producer", apply_bundle=lambda *args: self.fail("unreviewed mutation"),
            validate_current=lambda i, r, b: self.api.require_bundle_impact_review(i, r, b,
                producer_execution_id="EX-producer", input_snapshot="fixed-input"),
            validate_candidate=lambda *args: self.fail("unreviewed candidate"), publish=lambda *args: self.fail("unreviewed publication"))
        self.assertEqual("impact_review", result["bundles"][0]["next_owner"])
        self.assertEqual(self.request(), result["bundles"][0]["impact_review_request"])

    def test_review_evidence_does_not_change_the_mathematical_impact_plan(self):
        before = self.request()
        output = self.review_output(before)
        output["used_sources"] = [self.ids[0]]
        self.runtime["executions"]["EX-review"] = {"id": "EX-review", "role": "maintenance", "status": "ended",
            "action": {"role": "maintenance", "stage": "impact_review", "input_basis": {"impact_review": before}}, "output": output}
        self.assertEqual(before, self.request(), "Recording the review must not invalidate its own assigned impact plan")

    def test_review_resolver_uses_actual_git_bytes_and_scoped_receipt(self):
        import subprocess
        from do_math.git_store import GitStateStore
        from do_math.repository import canonical_json
        request = self.request()
        action = {"id": "AC-review", "role": "maintenance", "stage": "impact_review", "input_basis": {"impact_review": request}}
        output = self.review_output(request)
        fixed = {"action": action, "execution_id": "EX-review"}
        review_bundle = next(self.api.split_bundles(output, {}, fixed))
        self.runtime["executions"]["EX-review"] = {"id": "EX-review", "role": "maintenance", "actor_kind": "ai", "status": "running",
            "action": action, "output": output, "input_bundle": "BA-review-input"}
        self.runtime["integrations"] = {"IN-review": {"id": "IN-review", "execution_id": "EX-review",
            "payload_sha256": review_bundle["payload_sha256"],
            "response_sha256": exact_content_hash(self.api.member_values(output, {}, fixed)["output"])}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
            store = GitStateStore(root, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV")
            workspace = root / 'review-workspace'
            workspace.mkdir()
            artifacts = self.seal_review_fixture(self.runtime['executions']['EX-review'], output, fixed, workspace)
            head = store.publish(None, {"research/fixture.json": b"{}",
                "runtime/artifacts/BA-review-input/input/submission/context.json": canonical_json(fixed),
                **artifacts}).head
            args = {"producer_execution_id": "EX-producer", "input_snapshot": "fixed-input",
                "review_execution_id": "EX-review", "snapshot": head,
                "read_artifact": lambda snapshot, path: store.read_bytes(snapshot, path)}
            confirmations = self.api.require_bundle_impact_review(self.instance, self.runtime, self.bundle, **args)
            self.assertEqual(set(request["plans"]), set(confirmations))
            changed, running = self.api.apply_reviewed_knowledge_changes(self.instance, self.runtime, self.bundle,
                actor_ref="EX-producer", **args)
            self.assertEqual({self.ids[0], self.ids[2]},
                {row["supersedes"] for row in changed["knowledge"].values() if row.get("supersedes")})
            saved = store.publish(head, {"research/domain-result.json": canonical_json(changed),
                                        "runtime/domain-result.json": canonical_json(running)}).head
            self.assertEqual(changed, json.loads(store.read_bytes(saved, "research/domain-result.json")))
            retry_runtime = deepcopy(self.runtime)
            retry_runtime["executions"]["EX-retry"] = {"id": "EX-retry", "continuation_of": "EX-producer"}
            self.assertEqual(confirmations, self.api.require_bundle_impact_review(self.instance, retry_runtime,
                self.bundle, receiving_execution_id="EX-retry", **args))
            retry_runtime["executions"]["EX-retry"].pop("continuation_of")
            with self.assertRaises(ValueError):
                self.api.require_bundle_impact_review(self.instance, retry_runtime, self.bundle,
                    receiving_execution_id="EX-retry", **args)
            cached = deepcopy(self.runtime)
            cached['executions']['EX-review']['output']['summary'] = 'Untrusted cached projection'
            self.assertEqual(confirmations, self.api.require_bundle_impact_review(self.instance, cached, self.bundle, **args))
            for case in ("same_producer", "other_bundle", "stale", "unsealed", "tampered_output", "shared_conversation", "machine"):
                with self.subTest(case=case), self.assertRaises(ValueError):
                    i, r, b, a = deepcopy(self.instance), deepcopy(self.runtime), deepcopy(self.bundle), dict(args)
                    if case == "same_producer": a["review_execution_id"] = "EX-producer"
                    if case == "other_bundle": b["integration_id"] = "IN-other"
                    if case == "stale": i["knowledge"][self.ids[1]]["summary"] = "Changed premise"
                    if case == "unsealed": r["integrations"].clear()
                    if case == 'tampered_output':
                        output_ref = r['executions']['EX-review']['submission_intent']['output_ref']
                        a['read_artifact'] = lambda selected, path: (canonical_json({**output, 'summary': 'Altered'})
                            if path == output_ref else store.read_bytes(selected, path))
                    if case == "machine": r["executions"]["EX-review"]["actor_kind"] = "machine"
                    if case == "shared_conversation":
                        for identifier in ("EX-producer", "EX-review"):
                            r["executions"][identifier]["conversation_id"] = "same-conversation"
                    self.api.require_bundle_impact_review(i, r, b, **a)

            # A legally submitted negative judgment is evidence, never mutation permission.
            for decision in ("reject", "unresolved"):
                negative = deepcopy(output)
                negative["impact_review"]["plan_decisions"][0]["decision"] = decision
                self.api.validate_impact_review_response(request, negative)
                rejected_runtime = deepcopy(self.runtime)
                negative_id = 'EX-review-' + decision
                negative_input = 'BA-review-input-' + decision
                negative_fixed = {**deepcopy(fixed), 'execution_id': negative_id}
                negative_execution = {'id': negative_id, 'role': 'maintenance', 'actor_kind': 'ai',
                    'status': 'running', 'action': deepcopy(action), 'output': negative, 'input_bundle': negative_input}
                rejected_runtime['executions'][negative_id] = negative_execution
                negative_workspace = root / decision
                negative_workspace.mkdir()
                negative_artifacts = self.seal_review_fixture(negative_execution, negative, negative_fixed, negative_workspace)
                rejected_bundle = next(self.api.split_bundles(negative, {}, negative_fixed))
                rejected_runtime["integrations"]["IN-review"].update(
                    execution_id=negative_id,
                    payload_sha256=rejected_bundle["payload_sha256"],
                    response_sha256=exact_content_hash(self.api.member_values(negative, {}, negative_fixed)["output"]))
                negative_head = store.publish(saved, {**negative_artifacts,
                    'runtime/artifacts/' + negative_input + '/input/submission/context.json': canonical_json(negative_fixed)}).head
                with self.subTest(decision=decision), self.assertRaisesRegex(ValueError, "did not approve"):
                    self.api.require_bundle_impact_review(self.instance, rejected_runtime, self.bundle,
                        **{**args, "snapshot": negative_head, 'review_execution_id': negative_id})
                saved = negative_head

    def test_sealed_review_allows_real_domain_git_retry_and_rejects_wrong_evidence(self):
        import subprocess
        from do_math import activities, execution_profiles, model_policy
        from do_math.repository import ResearchRepository, canonical_json
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
            profiles = execution_profiles.build_profiles({"session_limits": model_policy.LIMITS,
                "tier_models": model_policy.MODELS, "observation_mode": "event_driven", "max_input_bytes": 500000,
                "effort": "medium", "operator_effort": "high", "operator_timeout_seconds": 600,
                "scholarly_enabled": True, "scholarly_server": None, "claude_only_assigned_model": False})
            self.instance.update({k: v for k, v in profiles.items() if k != "role_profile_refs"})
            self.runtime["queue"] = []
            def execution(identifier, role, action):
                aid = "AT-" + identifier.removeprefix("EX-")
                at = activities.open_activity(self.runtime, activity_id=aid, activity_kind=role,
                    owner_ref="task", input_refs=[], opened_at="2026-09-20T00:00:00Z")
                row = {"id": identifier, "role": role, "action": action, "actor_kind": "ai", "owner_activity_id": aid,
                    "created_at": "2026-09-20T00:00:00Z", "status": "running", "input_manifest": [], "context_origin": []}
                profile = next(p for p in profiles["execution_profiles"].values() if p["role"] == role)
                execution_profiles.bind_execution(row, profile)
                self.runtime["executions"][identifier] = row
                at["assigned_execution_ids"] = [identifier]
                return row
            execution("EX-producer", "research_work", {"id": "AC-producer", "role": "research_work", "target": None})
            repo = ResearchRepository(root, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV")
            head = repo.initialize(self.instance, self.runtime)
            self.runtime["executions"]["EX-producer"]["input_snapshot"] = head
            request = self.request()
            action = {"id": "AC-review", "role": "maintenance", "stage": "impact_review", "input_basis": {"impact_review": request}}
            reviewer = execution("EX-review", "maintenance", action)
            fixed = {"action": action, "execution_id": "EX-review", "snapshot": head,
                     "knowledge_catalog": [self.instance["knowledge"][kid] for kid in self.ids], "kind_definitions": {}}
            output = self.review_output(request)
            output["used_sources"] = [self.ids[0], self.ids[2]]
            from do_math import submission
            workspace = root / "review-workspace"
            workspace.mkdir()
            schema = contracts.schema_for("maintenance")
            schema["properties"]["impact_review"] = self.api.impact_review_response_schema(request)
            schema["required"].append("impact_review")
            submission.install_tools(workspace, fixed, schema, None)
            (workspace / "draft.json").write_bytes(canonical_json(output))
            sealed = submission.seal_submission(workspace, "draft.json", execution_id="EX-review",
                context=fixed, schema=schema, max_artifact_bytes=1024 * 1024)
            self.assertTrue(sealed["passed"], sealed["check"]["issues"])
            reviewer.update(input_bundle="BA-review-input", submitted_output_ref="runtime/artifacts/BA-review-output/output.json",
                            output=output, input_snapshot=head)
            artifacts = {"runtime/artifacts/BA-review-input/input/submission/context.json": canonical_json(fixed),
                         **{"runtime/artifacts/BA-review-output/" + path: raw
                            for path, raw in sealed["artifacts"].items()}}
            head = repo.save_with_state(head, self.instance, self.runtime, artifacts=artifacts)[0]
            def publish(i, r, bundle):
                nonlocal head
                head = repo.save_with_state(head, i, r)[0]
            def validate(i, r, bundle):
                repo.validate_candidate(i, r, head)
            def accept_review(i, r, bundle):
                from do_math.execution_lifecycle import record_submission_intent, transition_execution
                self.api.validate_impact_review_response(request, bundle["output"])
                record_submission_intent(r["executions"]["EX-review"],
                    {**sealed["intent"], "output_ref": reviewer["submitted_output_ref"],
                     'extensions_ref': 'runtime/artifacts/BA-review-output/extensions.json',
                     'check_ref': 'runtime/artifacts/BA-review-output/check.json'},
                    {"id": "CT-review", "kind": "submit_intent", "state": "accepted", "execution_id": "EX-review",
                     'payload': {'submission_check': {'artifacts': [
                         {'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
                         for path, raw in artifacts.items()]}}},
                    at="2026-09-20T00:00:01Z")
                transition_execution(r["executions"]["EX-review"], "ended", at="2026-09-20T00:00:02Z",
                    outcome="output_accepted", disposition={"kind": "submission_integrated"})
            review_result = self.api.apply_bundles(self.instance, self.runtime, output, {}, fixed,
                execution_id="EX-review", apply_bundle=accept_review,
                validate_current=lambda i, r, b: self.api.validate_impact_review_response(request, b["output"]),
                validate_candidate=validate, publish=publish)
            self.assertEqual("accepted", review_result["status"], review_result["bundles"])
            _, self.instance, self.runtime = repo.load(head)
            args = {"producer_execution_id": "EX-producer", "input_snapshot": request["input_snapshot"],
                    "review_execution_id": "EX-review", "snapshot": head,
                    "read_artifact": lambda selected, path: repo.read(path, selected)}
            confirmations = self.api.require_bundle_impact_review(self.instance, self.runtime, self.bundle, **args)
            self.assertEqual(set(request["plans"]), set(confirmations))
            for case in ("same_producer", "other_bundle", "stale", "unsealed"):
                with self.subTest(case=case), self.assertRaises(ValueError):
                    i, r, b, a = deepcopy(self.instance), deepcopy(self.runtime), deepcopy(self.bundle), dict(args)
                    if case == "same_producer": a["review_execution_id"] = "EX-producer"
                    if case == "other_bundle": b["integration_id"] = "IN-other"
                    if case == "stale": i["knowledge"][self.ids[1]]["summary"] = "Changed premise"
                    if case == "unsealed": r["integrations"].clear()
                    self.api.require_bundle_impact_review(i, r, b, **a)
            def apply_changes(i, r, b):
                updated, running = self.api.apply_reviewed_knowledge_changes(i, r, b,
                    actor_ref="EX-producer", **args)
                i.clear(); i.update(updated)
                r.clear(); r.update(running)
            result = self.api.apply_bundles(self.instance, self.runtime, self.output, self.extensions, context(),
                execution_id="EX-producer", apply_bundle=apply_changes,
                validate_current=lambda i, r, b: self.api.require_bundle_impact_review(i, r, b, **args),
                validate_candidate=validate, publish=publish)
            self.assertEqual("accepted", result["status"], result)
            saved, i, r = repo.load(head)
            self.assertEqual({self.ids[0], self.ids[2]}, {v["supersedes"] for v in i["knowledge"].values() if v.get("supersedes")})
            replay = self.api.apply_bundles(i, r, self.output, self.extensions, context(), execution_id="EX-producer",
                apply_bundle=lambda *a: self.fail("accepted bundle applied twice"),
                validate_current=lambda *a: self.fail("accepted bundle revalidated"),
                validate_candidate=validate, publish=lambda *a: self.fail("accepted bundle republished"))
            self.assertEqual("already_accepted", replay["bundles"][0]["status"])
            self.assertEqual(saved, head)


class ContractBoundaryTests(unittest.TestCase):
    def test_knowledge_change_cannot_self_confirm_its_impact(self):
        output = response()
        output["knowledge"] = []
        output["integration_bundles"] = [{"integration_id": "IN-change", "members": [
            "output", "activity-extensions.json/knowledge_changes/0"], "impact_set": [], "authority_refs": []}]
        ctx = {**context(), "execution_id": "EX-current", "knowledge_catalog": [{"id": "KN-source"}]}
        extensions = {"knowledge_changes": [{"id": "KN-source", "changes": {"statement": "Corrected"},
            "reason": "Correction", "impact_set": [], "independent_confirmation": {
                "plan_digest": "a" * 64, "decision": "approve", "review_ref": "RV-unknown",
                "reviewer_ref": "EX-current", "producer_ref": "EX-current", "affected_ids": []}}]}
        with tempfile.TemporaryDirectory() as directory:
            issues = submission.payload_issues(output, contracts.schema_for("research_work"), ctx, extensions, Path(directory))
        self.assertTrue(any(row["rule_id"] == "schema.additionalProperties"
                            and row["path"].startswith("activity-extensions.json/knowledge_changes/0")
                            for row in issues), issues)

    def test_central_capture_uses_exact_current_draft_after_optional_local_check(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace=Path(directory);ctx={**context(),'execution_id':'EX-1'}
            schema=contracts.schema_for('research_work')
            submission.install_tools(workspace,ctx,schema,None)
            draft=workspace/'draft.json';draft.write_bytes(canonical_json(response()))
            producer=submission.producer_check(workspace,draft)
            changed=draft.read_bytes()+b' \r\n';draft.write_bytes(changed)
            sealed=submission.seal_submission(workspace,'draft.json',execution_id='EX-1',context=ctx,
                schema=schema,max_artifact_bytes=1024*1024)
            self.assertTrue(sealed['passed'],sealed['check']['issues'])
            self.assertEqual(sealed['artifacts']['output.json'],changed)
            self.assertNotEqual(sealed['intent']['output_sha256'],producer['output_sha256'])

    def test_central_check_uses_issued_schema_despite_local_tool_mutation(self):
        for relative in ('input/submission/schema.json','input/tools/submission-support.zip'):
            with self.subTest(path=relative),tempfile.TemporaryDirectory() as directory:
                workspace=Path(directory);ctx={**context(),'execution_id':'EX-1'}
                schema=contracts.schema_for('research_work')
                submission.install_tools(workspace,ctx,schema,None)
                (workspace/'draft.json').write_bytes(canonical_json(response()))
                (workspace/relative).write_bytes(b'broken optional local tool input')
                sealed=submission.seal_submission(workspace,'draft.json',execution_id='EX-1',
                    context=ctx,schema=schema,max_artifact_bytes=1024*1024)
                self.assertTrue(sealed['passed'],sealed['check']['issues'])
                self.assertEqual(sealed['check']['schema_ref'],contracts.schema_reference(schema))

    def test_central_rejection_preserves_malformed_draft_and_available_sidecar(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace=Path(directory);ctx={**context(),'execution_id':'EX-1'}
            schema=contracts.schema_for('research_work')
            submission.install_tools(workspace,ctx,schema,None)
            raw=b'{broken original output';sidecar=b'{broken original sidecar'
            (workspace/'draft.json').write_bytes(raw)
            (workspace/'activity-extensions.json').write_bytes(sidecar)
            (workspace/'checks').mkdir(exist_ok=True)
            (workspace/'checks/broken.json').write_bytes(b'{broken optional local diagnostic')
            sealed=submission.seal_submission(workspace,'draft.json',execution_id='EX-1',
                context=ctx,schema=schema,max_artifact_bytes=1024*1024)
            self.assertFalse(sealed['passed'])
            self.assertEqual(sealed['artifacts']['output.json'],raw)
            self.assertEqual(sealed['artifacts']['extensions.json'],sidecar)
            self.assertEqual(sealed['check']['issues'][0]['rule_id'],'submission.parse')

    def test_producer_check_binds_exact_schema_and_raw_output_on_parse_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            ctx = context()
            ctx["execution_id"] = "EX-1"
            schema = contracts.schema_for("research_work")
            submission.install_tools(workspace, ctx, schema, None)
            draft = workspace / "broken.json"
            draft.write_bytes(b'{broken')
            result = submission.producer_check(workspace, draft)
            self.assertFalse(result["passed"])
            self.assertEqual(contracts.schema_reference(schema), result["schema_ref"])
            self.assertEqual(hashlib.sha256(b'{broken').hexdigest(), result["output_sha256"])
            self.assertEqual("broken.json", result["raw_output_path"])
            self.assertEqual(b'{broken', draft.read_bytes())

    def test_central_preview_does_not_disclose_private_candidate_or_exception(self):
        module = self.integration()
        private = {"private_reviews": {"secret-review": {"decision": "secret-judgment"}}}
        with tempfile.TemporaryDirectory() as directory:
            def reject(*args):
                raise ValueError("secret-review secret-judgment")
            result = submission.preview_submission(response(), contracts.schema_for("research_work"),
                context(), {}, Path(directory), execution_id="EX-1", tool_sha256="same",
                instance=private, runtime={}, apply_bundle=reject,
                validate_current=lambda *a: None, validate_candidate=lambda *a: None)
            self.assertNotIn("secret-", json.dumps(result))
            self.assertNotIn("instance", result)
            self.assertNotIn("runtime", result)
            self.assertEqual({"private_reviews": {"secret-review": {"decision": "secret-judgment"}}}, private)
            self.assertFalse(result["passed"])

    def test_intent_source_coverage_is_checked_before_independent_review(self):
        action = {"role": "intent_interpretation", "stage": "interpret"}
        ctx = {**context(), "action": action, "user_request": {"id": "UC-1", "text": "첫째 둘째"}}
        output = dict(summary="interpret", used_sources=[], questions=[], question_details=[], needs_clarification=False,
            import_units=[dict(unit_id="IU-1", source_range={"start": 0, "end": 2}, interpretation="첫째",
                owner_kind="charter", owner_ref="context:goal", payload={}, decision_refs=[], question_refs=[])],
            integration_bundles=[dict(integration_id="IN-1", members=["output"], impact_set=[], authority_refs=[])])
        with tempfile.TemporaryDirectory() as directory:
            schema = contracts.action_schema(action)
            issues = submission.payload_issues(output, schema, ctx, {}, Path(directory))
            self.assertTrue(any(row["rule_id"] == "intent.source_coverage" for row in issues))
            output["import_units"][0]["source_range"]["end"] = len(ctx["user_request"]["text"])
            self.assertEqual([], submission.payload_issues(output, schema, ctx, {}, Path(directory)))

    def test_contract_review_evidence_must_be_supplied(self):
        output = dict(summary="review", used_sources=[], questions=[], item_reviews=[
            dict(item_id=item, decision="approved", evidence_refs=["MISSING"], findings=[], missing_inputs=[], next_owner="research")
            for item in contracts.CONTRACT_REVIEW_ITEMS],
            integration_bundles=[dict(integration_id="IN-1", members=["output"], impact_set=[], authority_refs=[])])
        ctx = {**context(), "action": {"role": "task_contract_review"}}
        with tempfile.TemporaryDirectory() as directory:
            issues = submission.payload_issues(output, contracts.schema_for("task_contract_review"), ctx, {}, Path(directory))
            self.assertTrue(any(row["rule_id"] == "submission.explicit_reference" for row in issues))

    def test_plan_schema_has_one_population_disposition_list(self):
        props = contracts.schema_for("research_plan")["properties"]
        self.assertIn("dispositions", props)
        self.assertNotIn("selections", props)
        self.assertNotIn("deferred", props)

    def test_scope_planning_schema_reaches_domain_scope_validator(self):
        props = contracts.action_schema({"role": "identity_review", "stage": "scope"})["properties"]
        self.assertIn("scope_assessment", props)

    def test_machine_check_compares_checkpoint_failures_in_both_modes(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            ctx = context()
            submission.install_tools(workspace, ctx, contracts.schema_for("research_work"), None)
            (workspace / "checkpoint.json").write_text('{}', encoding="utf-8")
            args = (response(), contracts.schema_for("research_work"), ctx, {}, workspace)
            producer = submission.check_submission(*args, mode="producer", execution_id="EX-1", tool_sha256="same")
            receiver = submission.check_submission(*args, mode="receiver", execution_id="EX-1", tool_sha256="same", previous=producer)
            self.assertFalse(producer["passed"])
            self.assertTrue(any(row["path"] == "checkpoint.json" for row in producer["issues"]))
            self.assertEqual("matched", receiver["comparison"]["status"])

    def test_installed_zip_runs_and_seals_real_producer_check(self):
        import subprocess
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            ctx = context()
            ctx["execution_id"] = "EX-1"
            submission.install_tools(workspace, ctx, contracts.schema_for("research_work"), None)
            (workspace / "response.json").write_text(json.dumps(response()), encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", "input/tools/check_submission.py", "--output", "response.json"],
                                    cwd=workspace, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            record = json.loads(result.stdout)
            self.assertTrue(record["passed"])
            self.assertEqual(record, json.loads((workspace / "checks" / (record["id"] + ".json")).read_bytes()))

    def test_parse_failure_is_sealed_without_discarding_original_bytes(self):
        import subprocess
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            ctx = context()
            submission.install_tools(workspace, ctx, contracts.schema_for("research_work"), None)
            draft = workspace / "response.json"
            original = b'{"broken":'
            draft.write_bytes(original)
            result = subprocess.run([sys.executable, "-B", "input/tools/check_submission.py", "--output", "response.json"],
                                    cwd=workspace, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(1, result.returncode)
            self.assertEqual(original, draft.read_bytes())
            records = list((workspace / "checks").glob("*.json"))
            self.assertEqual(1, len(records))
            self.assertIn("schema", json.loads(records[0].read_bytes())["not_checked"])

    def test_check_summary_preserves_unresolved_failures_outside_window(self):
        self.assertTrue(hasattr(submission, "summarize_checks"))
        failure = self.integration().issue("schema.required", "output/report", "missing", "IN-A")
        records = [dict(id="MC-old", execution_id="EX-old", tool_sha256="tool", issues=[failure], repairs=[], passed=False),
                   dict(id="MC-new", execution_id="EX-new", tool_sha256="tool", issues=[], repairs=[], passed=True)]
        result = submission.summarize_checks(records, history_window=1)
        self.assertEqual(1, result["window_check_count"])
        self.assertEqual(failure["issue_id"], result["unresolved"][0]["issue_id"])


    def test_comparison_uses_fixed_context_not_unreferenced_local_input_files(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "input").mkdir()
            path = workspace / "input" / "evidence.txt"
            path.write_text("before", encoding="utf-8")
            args = (response(), contracts.schema_for("research_work"), context(), {}, workspace)
            before = submission.check_submission(*args, mode="producer", execution_id="EX-1", tool_sha256="same")
            path.write_text("after", encoding="utf-8")
            after = submission.check_submission(*args, mode="receiver", execution_id="EX-1", tool_sha256="same", previous=before)
            self.assertEqual("matched", after["comparison"]["status"])
            changed_context = {**args[2], "snapshot": "new-authoritative-input"}
            changed = submission.check_submission(args[0], args[1], changed_context, {}, workspace,
                mode="receiver", execution_id="EX-1", tool_sha256="same", previous=before)
            self.assertEqual("input_changed", changed["comparison"]["status"])

    def test_bundle_receipt_and_records_share_real_git_publication(self):
        import subprocess
        from do_math import activities, execution_profiles, model_policy, knowledge_io
        from do_math.repository import ResearchRepository
        from do_math.state_contract import StateContract
        module = self.integration()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
            contract = StateContract.default()
            repo = ResearchRepository(root, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV", contract=contract)
            profile_state = execution_profiles.build_profiles({
                "session_limits": model_policy.LIMITS, "tier_models": model_policy.MODELS,
                "observation_mode": "event_driven", "max_input_bytes": 500000,
                "effort": "medium", "operator_effort": "high", "operator_timeout_seconds": 600,
                "scholarly_enabled": True, "scholarly_server": None, "claude_only_assigned_model": False})
            instance = {"feature_version": 5, "knowledge": {}, "expositions": {},
                        **{k: v for k, v in profile_state.items() if k != "role_profile_refs"}}
            instance = knowledge_io.ensure_ontology(instance)
            runtime = {"feature_version": 5, "executions": {}}
            activity = activities.open_activity(runtime, activity_id="AT-1", activity_kind="research_work",
                owner_ref="task", input_refs=[], opened_at="2026-09-20T00:00:00Z")
            profile = next(p for p in instance["execution_profiles"].values() if p["role"] == "research_work")
            execution = {"id": "EX-1", "role": "research_work", "actor_kind": "ai", "owner_activity_id": "AT-1",
                "created_at": "2026-09-20T00:00:00Z", "status": "running", "input_manifest": [], "context_origin": []}
            execution_profiles.bind_execution(execution, profile)
            runtime["executions"]["EX-1"] = execution
            activity["assigned_execution_ids"] = ["EX-1"]
            head = repo.initialize(instance, runtime)
            def publish(i, r, bundle):
                nonlocal head
                head = repo.save_with_state(head, i, r)[0]
            def apply(i, r, bundle):
                for record in bundle["output"]["knowledge"]:
                    updated, running, _ = knowledge_io.import_candidate(i, r, record,
                        source_ref="EX-1", actor_ref="EX-1")
                    i.clear()
                    i.update(updated)
                    r.clear()
                    r.update(running)
            def validate(i, r, bundle):
                repo.validate_candidate(i, r, head)
            before = deepcopy((instance, runtime))
            preview = module.preview_bundles(instance, runtime, response(), {}, context(), execution_id="EX-1",
                apply_bundle=apply, validate_current=lambda *a: None, validate_candidate=validate)
            self.assertEqual("accepted", preview["status"], preview)
            self.assertEqual(before, (instance, runtime))
            self.assertEqual(head, repo._store.read_snapshot().head)
            first = response()
            first["knowledge"][1]["kind"] = "undefined_kind"
            result = module.apply_bundles(instance, runtime, first, {}, context(), execution_id="EX-1",
                apply_bundle=apply, validate_current=lambda *a: None, validate_candidate=validate, publish=publish)
            self.assertEqual("partial", result["status"], result)
            self.assertEqual(["IN-B"], result["retry_bundle_ids"])
            _, partial_instance, partial_runtime = repo.load()
            self.assertEqual({"A"}, {row["title"] for row in partial_instance["knowledge"].values()})
            receipt = partial_runtime["integrations"]["IN-A"]
            retry = response()
            retry["knowledge"] = [knowledge("B")]
            retry["integration_bundles"] = [{"integration_id": "IN-B", "members": ["output/knowledge/0"],
                                              "impact_set": [], "authority_refs": []}]
            retry_context = {**context(), "accepted_response": {"integration_id": receipt["id"],
                                                                "response_sha256": receipt["response_sha256"]}}
            result = module.apply_bundles(partial_instance, partial_runtime, retry, {}, retry_context, execution_id="EX-1",
                apply_bundle=apply, validate_current=lambda *a: None, validate_candidate=validate, publish=publish)
            saved_head, saved_instance, saved_runtime = repo.load()
            self.assertEqual("accepted", result["status"], result["bundles"])
            self.assertEqual(head, saved_head)
            self.assertEqual({"A", "B"}, {row["title"] for row in saved_instance["knowledge"].values()})
            self.assertEqual({"IN-A", "IN-B"}, set(saved_runtime["integrations"]))
            parent = subprocess.check_output(["git", "-C", str(root), "rev-parse", head + "^"], text=True).strip()
            _, parent_instance, parent_runtime = repo.load(parent)
            self.assertEqual({"A"}, {row["title"] for row in parent_instance["knowledge"].values()})
            self.assertEqual({"IN-A"}, set(parent_runtime["integrations"]))


    def test_structured_task_candidate_has_one_completion_authority(self):
        props = contracts.schema_for("research_preparation")["properties"]["candidates"]["items"]["properties"]
        self.assertIn("completion_obligations", props)
        self.assertNotIn("completion_criteria", props)
        self.assertEqual("object", props["scope"]["type"])

    def test_operational_response_uses_six_dispositions(self):
        props = contracts.schema_for("operational_review")["properties"]
        self.assertIn("disposition", props)
        self.assertNotIn("decision", props)

    def test_same_response_can_propose_a_kind_definition(self):
        props = submission.extension_schema(context()["action"])["properties"]
        self.assertIn("kind_definitions", props)

    def test_specialized_role_schema_uses_same_envelope(self):
        from do_math import governance
        schema = contracts.action_schema({"role": "intent_interpretation", "stage": "check"})
        expected = governance.interpretation_schema("check")
        self.assertTrue(set(expected["properties"]) <= set(schema["properties"]))
        self.assertIn("integration_bundles", schema["properties"])
        self.assertNotIn("integration_bundles", schema["required"])

    def test_preview_records_are_written_even_when_schema_is_invalid(self):
        import contextlib
        import io
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            ctx = context()
            submission.install_tools(workspace, ctx, contracts.schema_for("research_work"), None)
            draft = workspace / "response.json"
            draft.write_text('{}', encoding="utf-8")
            with patch.object(Path, "cwd", return_value=workspace), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(1, submission.main(["--output", str(draft)]))
            records = list((workspace / "checks").glob("*.json"))
            self.assertEqual(1, len(records))
            check = json.loads(records[0].read_bytes())
            self.assertIn("payload_semantics", check["not_checked"])

    def test_local_schema_failure_does_not_block_valid_bundle(self):
        output = response()
        del output["knowledge"][1]["statement"]
        with tempfile.TemporaryDirectory() as directory:
            issues = submission.payload_issues(output, contracts.schema_for("research_work"), context(), {}, Path(directory))
        self.assertEqual({"IN-B"}, {row.get("integration_id") for row in issues})
        result = self.integration().apply_bundles({}, {}, output, {}, context(), execution_id="EX-1",
            apply_bundle=lambda i, r, b: i.update({b["integration_id"]: True}),
            validate_current=lambda *a: None, validate_candidate=lambda *a: None, publish=lambda *a: None,
            submission_issues=issues)
        self.assertEqual({"IN-A": True}, result["instance"])

    def test_valid_schema_bundle_is_semantically_checked_even_with_invalid_sibling(self):
        output = response()
        output["knowledge"][0]["statement"] = ""
        del output["knowledge"][1]["statement"]
        with tempfile.TemporaryDirectory() as directory:
            issues = submission.payload_issues(output, contracts.schema_for("research_work"), context(), {}, Path(directory))
        self.assertEqual({"IN-A", "IN-B"}, {row.get("integration_id") for row in issues})

    def test_structural_failure_never_crashes_on_wrong_record_type(self):
        output = response()
        output["knowledge"][0] = None
        issues = self.integration().inspect_bundles(output, {}, context())
        self.assertIsInstance(issues, list)

    def test_malformed_metadata_returns_its_bundle_without_losing_independent_output(self):
        for value in (None, [], 1, 'invalid', {'title': []}):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                output = response()
                output['integration_bundles'][0]['members'].append(
                    'activity-extensions.json/knowledge_metadata/0')
                extensions = {'knowledge_metadata': [value]}
                issues = submission.payload_issues(output, contracts.schema_for('research_work'),
                    context(), extensions, Path(directory))
                self.assertTrue(issues)
                self.assertEqual({row['integration_id'] for row in issues}, {'IN-A'})
                self.assertTrue(all(row['rule_id'] == 'schema.type' for row in issues), issues)
                self.assertTrue(all(row['path'].startswith(
                    'activity-extensions.json/knowledge_metadata/0') for row in issues))
                self.assertTrue(submission.capture_eligible(output, extensions, context(), issues))

    def test_structural_top_level_failure_returns_without_candidate_application(self):
        for output, extensions in ((None, {}), ([], {}), (response(), [])):
            with self.subTest(output=type(output).__name__, extensions=type(extensions).__name__):
                result = self.integration().apply_bundles({"original": True}, {}, output, extensions, context(),
                    execution_id="EX-1", apply_bundle=lambda *a: self.fail("Malformed candidate applied"),
                    validate_current=lambda *a: self.fail("Malformed candidate validated"),
                    validate_candidate=lambda *a: self.fail("Malformed candidate validated"),
                    publish=lambda *a: self.fail("Malformed candidate published"))
                self.assertEqual("returned", result["status"])
                self.assertTrue(result["issues"])
                self.assertEqual({"original": True}, result["instance"])

    def test_proposed_kind_and_consumer_must_share_bundle(self):
        output = response()
        output["knowledge"][0]["kind"] = "experiment"
        output["integration_bundles"][1]["members"].append("activity-extensions.json/kind_definitions/0")
        extensions = {"kind_definitions": [{"family": "knowledge", "token": "experiment", "meaning": "experiment", "constraints": {}}]}
        issues = self.integration().inspect_bundles(output, extensions, context())
        self.assertIn("integration.reference_closure", {row["rule_id"] for row in issues})

    def test_preview_applies_candidate_without_publishing_or_mutating_input(self):
        module = self.integration()
        self.assertTrue(hasattr(module, "preview_bundles"))
        original = {}
        preview = module.preview_bundles(original, {}, response(), {}, context(), execution_id="EX-1",
            apply_bundle=lambda i, r, b: i.update({b["integration_id"]: True}),
            validate_current=lambda *a: None, validate_candidate=lambda *a: None)
        self.assertEqual({}, original)
        self.assertEqual({"IN-A": True, "IN-B": True}, preview["instance"])
        self.assertEqual("preview", preview["mode"])

    def test_installed_receipt_family_checks_execution_ref(self):
        from do_math.state_contract import StateContract
        family = StateContract.default().family("runtime", "integrations")
        self.assertIsNotNone(family)
        self.assertEqual({("EX-1", "executions")}, set(family.references({"execution_id": "EX-1"})))


    def integration(self):
        self.assertTrue((Path(submission.__file__).with_name("integration.py")).exists(),
                        "bundle application must exist, not just response metadata")
        return importlib.import_module("do_math.integration")

    def test_manifest_is_optional_but_explicit_declarations_remain_typed(self):
        schema = contracts.schema_for("research_work")
        self.assertNotIn("integration_bundles", schema["required"])
        validator = __import__("jsonschema").Draft202012Validator(schema)
        output = response(); output.pop("integration_bundles")
        self.assertEqual(list(validator.iter_errors(output)), [])
        for value in (None, [], [{}]):
            with self.subTest(value=value):
                self.assertTrue(list(validator.iter_errors({**output, "integration_bundles": value})))

    def test_operational_review_can_request_contract_revision(self):
        schema = submission.extension_schema({"role": "operational_review"})
        self.assertIn("revision_requests", schema["properties"])

    def test_valid_bundles_pass_same_preview_checker(self):
        with tempfile.TemporaryDirectory() as directory:
            issues = submission.payload_issues(response(), contracts.schema_for("research_work"),
                                               context(), {}, Path(directory))
        self.assertEqual([], issues)

    def test_missing_member_is_rejected(self):
        output = response()
        output["integration_bundles"][1]["members"] = ["output/relations/0"]
        issues = self.integration().inspect_bundles(output, {}, context())
        self.assertIn("integration.members", {row["rule_id"] for row in issues})

    def test_cross_bundle_new_reference_requires_merge(self):
        output = response()
        output["knowledge"][1]["dependencies"] = ["A"]
        issues = self.integration().inspect_bundles(output, {}, context())
        self.assertIn("integration.reference_closure", {row["rule_id"] for row in issues})

    def test_metadata_cannot_split_from_its_new_record(self):
        output = response()
        output["integration_bundles"][1]["members"].append("activity-extensions.json/knowledge_metadata/0")
        issues = self.integration().inspect_bundles(output, {"knowledge_metadata": [{"title": "A"}]}, context())
        self.assertIn("integration.reference_closure", {row["rule_id"] for row in issues})

    def test_plan_is_one_bundle(self):
        output = response()
        ctx = context()
        ctx["action"]["role"] = "research_plan"
        issues = self.integration().inspect_bundles(output, {}, ctx)
        self.assertIn("integration.single_bundle", {row["rule_id"] for row in issues})

    def test_failed_candidate_does_not_undo_other_bundle(self):
        module = self.integration()
        original = {"knowledge": {}}
        publications = []
        def apply(instance, runtime, bundle):
            for record in bundle["output"]["knowledge"]:
                instance["knowledge"][record["title"]] = record
        def validate(instance, runtime, bundle):
            if "B" in instance["knowledge"]:
                raise ValueError("B rejected")
        result = module.apply_bundles(original, {}, response(), {}, context(), execution_id="EX-1",
            apply_bundle=apply, validate_candidate=validate, validate_current=lambda *a: None,
            publish=lambda i, r, b: publications.append(deepcopy(i)))
        self.assertEqual(["accepted", "returned"], [r["status"] for r in result["bundles"]])
        self.assertEqual({"A"}, set(result["instance"]["knowledge"]))
        self.assertEqual({"knowledge": {}}, original)
        self.assertEqual(1, len(publications))
        self.assertIn("IN-B", result["retry_bundle_ids"])
        self.assertEqual(result["bundles"][1]["issues"], result["issues"])

    def test_receipt_is_published_with_state_and_replay_has_no_effect(self):
        module = self.integration()
        published = []
        calls = []
        kwargs = dict(execution_id="EX-1", apply_bundle=lambda i, r, b: calls.append(b["integration_id"]),
                      validate_candidate=lambda *a: None, validate_current=lambda *a: None,
                      publish=lambda i, r, b: published.append(deepcopy(r)))
        first = module.apply_bundles({}, {}, response(), {}, context(), **kwargs)
        self.assertIn("IN-A", published[0]["integrations"])
        second = module.apply_bundles(first["instance"], first["runtime"], response(), {}, context(), **kwargs)
        self.assertEqual(2, len(calls))
        self.assertTrue(all(r["status"] == "already_accepted" for r in second["bundles"]))

    def test_retry_only_failed_bundle_does_not_repeat_response_finalization(self):
        module = self.integration()
        output = response()
        base = module.member_values(output, {}, context())["output"]
        output["knowledge"] = [output["knowledge"][1]]
        output["integration_bundles"] = [dict(integration_id="IN-B", members=["output/knowledge/0"], impact_set=[], authority_refs=[])]
        ctx = {**context(), "accepted_response": {"integration_id": "IN-A", "response_sha256": exact_content_hash(base)}}
        self.assertEqual([], module.inspect_bundles(output, {}, ctx))
        calls = []
        result = module.apply_bundles({}, {}, output, {}, ctx, execution_id="EX-2",
            apply_bundle=lambda i, r, b: calls.append(b["owns_response"]),
            validate_current=lambda *a: None, validate_candidate=lambda *a: None, publish=lambda *a: None)
        self.assertEqual("accepted", result["status"])
        self.assertEqual([False], calls)

    def test_current_authority_failure_precedes_mutation(self):
        module = self.integration()
        calls = []
        def denied(*args):
            raise ValueError("authority revoked")
        result = module.apply_bundles({}, {}, response(), {}, context(), execution_id="EX-1",
            apply_bundle=lambda *a: calls.append(1), validate_candidate=lambda *a: None,
            validate_current=denied, publish=lambda *a: calls.append(2))
        self.assertEqual([], calls)
        self.assertEqual(["IN-A", "IN-B"], result["retry_bundle_ids"])

    def test_publish_failure_does_not_claim_acceptance(self):
        module = self.integration()
        def conflict(*args):
            raise ValueError("CAS conflict")
        result = module.apply_bundles({}, {}, response(), {}, context(), execution_id="EX-1",
            apply_bundle=lambda i, r, b: i.update(changed=True), validate_candidate=lambda *a: None,
            validate_current=lambda *a: None, publish=conflict)
        self.assertEqual({}, result["instance"])
        self.assertFalse(result["runtime"].get("integrations"))
        self.assertTrue(all(r["status"] == "returned" for r in result["bundles"]))

    def test_machine_checks_compare_exact_inputs_and_preserve_skipped_checks(self):
        self.assertTrue(hasattr(submission, "check_submission"))
        with tempfile.TemporaryDirectory() as directory:
            args = (response(), contracts.schema_for("research_work"), context(), {}, Path(directory))
            producer = submission.check_submission(*args, mode="producer", execution_id="EX-1", tool_sha256="same")
            receiver = submission.check_submission(*args, mode="receiver", execution_id="EX-1", tool_sha256="same", previous=producer)
            self.assertEqual("matched", receiver["comparison"]["status"])
            forged = deepcopy(producer)
            forged["issues"] = [{"rule_id": "x", "path": "output", "issue_id": "x", "message": "x"}]
            receiver = submission.check_submission(*args, mode="receiver", execution_id="EX-1", tool_sha256="same", previous=forged)
            self.assertEqual("tool_defect", receiver["comparison"]["status"])
            malformed = submission.check_submission({}, contracts.schema_for("research_work"), context(), {}, Path(directory),
                mode="producer", execution_id="EX-1", tool_sha256="same")
            self.assertIn("payload_semantics", malformed["not_checked"])
            self.assertTrue(all("issue_id" in row and "rule_id" in row for row in malformed["issues"]))



class DefaultBundleTests(unittest.TestCase):
    def setUp(self):
        from do_math import integration
        self.api = integration
        self.context = {**context(), "execution_id": "EX-default", "action": {
            "id": "AC-default", "role": "research_work", "grant_id": "GR-default"},
            "grants": [{"id": "GR-default"}]}
        self.output = response()
        self.output.pop("integration_bundles")

    def test_missing_manifest_is_one_deterministic_unit_without_editing_original(self):
        before = deepcopy(self.output)
        self.assertEqual(self.api.inspect_bundles(self.output, {}, self.context), [])
        bundles = list(self.api.split_bundles(self.output, {}, self.context))
        self.assertEqual(len(bundles), 1)
        self.assertEqual(set(bundles[0]["members"]), {"output", "output/knowledge/0", "output/knowledge/1"})
        self.assertEqual(bundles[0]["authority_refs"], ["GR-default"])
        self.assertEqual(bundles[0]["impact_set"], [])
        self.assertEqual(self.output, before)
        self.assertEqual(bundles, list(self.api.split_bundles(deepcopy(self.output), {}, deepcopy(self.context))))
        changed = deepcopy(self.output); changed["report"] += " updated"
        self.assertNotEqual(bundles[0]["integration_id"], list(self.api.split_bundles(changed, {}, self.context))[0]["integration_id"])
        changed_context = {**self.context, "execution_id": "EX-other"}
        self.assertNotEqual(bundles[0]["integration_id"], list(self.api.split_bundles(self.output, {}, changed_context))[0]["integration_id"])

    def test_revision_and_partial_acceptance_still_require_explicit_declarations(self):
        cases = [({}, {**self.context, "accepted_integration_ids": ["IN-earlier"]}),
                 ({}, {**self.context, "accepted_response": {"response_sha256": "a" * 64}}),
                 ({}, {**self.context, "action": {**self.context["action"], "revision_targets": ["TK-old"]}}),
                 ({"knowledge_changes": [{"id": "KN-old"}]}, self.context),
                 ({"task_dispositions": [{"task_id": "TK-old"}]}, self.context)]
        for extensions, ctx in cases:
            with self.subTest(extensions=extensions, context=ctx):
                self.assertTrue(self.api.inspect_bundles(self.output, extensions, ctx))
        preparation = {"candidates": [{"revises_task_id": "TK-old"}]}
        self.assertTrue(self.api.inspect_bundles(preparation, {}, self.context))

    def test_explicit_split_stays_split_and_orphan_impact_fails_structurally(self):
        output = response()
        self.assertEqual(len(list(self.api.split_bundles(output, {}, self.context))), 2)
        self.assertEqual(self.api.inspect_bundles(output, {}, self.context), [])
        output["integration_bundles"][0]["impact_set"] = ["read-source"]
        issues = self.api.inspect_bundles(output, {}, self.context)
        self.assertTrue(any(r["rule_id"] == "integration.mutation_root" and r["integration_id"] == "IN-A" for r in issues), issues)
        self.assertEqual(output["integration_bundles"][0]["impact_set"], ["read-source"])


if __name__ == "__main__":
    unittest.main()
