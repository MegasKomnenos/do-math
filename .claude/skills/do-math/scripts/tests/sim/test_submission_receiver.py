"""The engine's central receiver on a Sim: sealed receipts, previews, bundle application, receipts and waits.

Every engine method runs on the Sim's real engine and store (``support.submission_receiver``).
The legacy tests replaced the store with autospec doubles, stubbed the domain
callbacks (``_apply``, ``_validate_bundle_current``, ``_apply_submission_bundles``,
``_record_task_receipt``, ``_save``) or patched ``read_sealed_submission``;
here those run for real, so each test passes the points the legacy test cut.
Calls the legacy tests counted through their doubles are observed on the
unchanged product with ``ObservedCalls``; publication failures come from the
Git port (a held ref lock), not from a replaced publisher.
"""
from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path
import shutil
import unittest

from do_math import integration, knowledge, knowledge_io, submission
from do_math.canonical import canonical_json
from do_math.engine import ResearchEngine
from do_math.repository import ResearchRepository
from support.knowledge_builders import knowledge_candidate
from support.role_answers import seal_response
from support.engine_context import damage
from support.engine_context import assert_result_documents
from support.provider_probes import ObservedCalls
from support.sim import Sim, warm_template
from support.submission_receiver import held_ref, history, order, receive, research, submit

setUpModule = warm_template


class CentralSubmissionHistoryTests(unittest.TestCase):
    def setUp(self):
        self.scene = history()

    def test_orphan_impact_is_returned_then_default_bundle_preserves_raw_git_input(self):
        scene = self.scene
        action = scene.action
        bad = deepcopy(scene.output)
        bad["integration_bundles"][0]["impact_set"] = ["read-source"]
        _, rejected = submit(scene, "CT-impact", canonical_json(bad))
        self.assertEqual(rejected["state"], "rejected", rejected)
        self.assertEqual(scene.engine.runtime["executions"]["EX-history"]["status"], "running")
        summary = scene.engine._submission_check_summary(scene.engine.head, scene.engine.runtime)
        self.assertTrue(any(row["rule_id"] == "integration.mutation_root" for row in summary["unresolved"]), summary)
        output = {k: v for k, v in scene.output.items() if k != "integration_bundles"}
        output["report"] = "\uc870\ud569 e\u0301 \u00b7 \u00e9 \u00b7 \ud55c\uae00 \u00b7 \U0001f600\n exact original"
        raw = json.dumps(output, ensure_ascii=False, indent=3).encode("utf-8")
        _, accepted = submit(scene, "CT-default", raw)
        self.assertEqual(accepted["state"], "accepted", accepted)
        scene.sim.restart()
        engine = scene.engine
        execution = engine.runtime["executions"]["EX-history"]
        stored = engine.store.read(execution["submission_intent"]["output_ref"], engine.head)
        self.assertEqual(stored, raw)
        restored = submission.load_json(stored)
        self.assertNotIn("integration_bundles", restored)
        fixed = submission.load_json(engine.store.read(
            "runtime/artifacts/BA-history-input/input/submission/context.json", engine.head))
        before = list(integration.split_bundles(output, {}, scene.context))
        after = list(integration.split_bundles(restored, {}, fixed))
        self.assertEqual(before, after)
        self.assertEqual(len(after), 1)
        self.assertEqual(after[0]["authority_refs"], [action["grant_id"]])
        result = engine._apply_submission_bundles(action, restored, {}, "EX-history", fixed, [])
        self.assertEqual(result["status"], "accepted", result["issues"])
        self.assertEqual(len(result["bundles"]), 1)
        _, _, saved = engine.store.load()
        self.assertIn(after[0]["integration_id"], saved["integrations"])
        self.assertEqual(engine.store.read(execution["submission_intent"]["output_ref"], engine.head), raw)

    def test_rejected_corrected_replayed_and_snapshot_bound_central_checks(self):
        from support.entry import entry
        _entry = entry()
        scene = self.scene
        # The public activation already sealed its own central checks; count the seals this test adds to them.
        base = scene.engine._submission_check_summary(scene.engine.head, scene.engine.runtime)
        self.assertEqual((base['status'], base['unresolved']), ('verified', []), base)
        bad = canonical_json({k: v for k, v in scene.output.items() if k != 'report'})
        request, rejected = submit(scene, 'CT-bad', bad)
        self.assertEqual(rejected['state'], 'rejected', rejected)
        self.assertTrue(rejected.get('publication_id'), rejected)
        engine = scene.engine
        first_head = engine.head
        self.assertEqual(engine.runtime['executions']['EX-history']['status'], 'running')
        self.assertNotIn('authority_revocation', engine.runtime['executions']['EX-history'])
        first = engine._submission_check_summary(first_head, engine.runtime)
        self.assertEqual(first['status'], 'verified', first)
        self.assertEqual(first['seal_count'], base['seal_count'] + 1)
        self.assertTrue(first['unresolved'])
        stored = next(r for r in engine.runtime['control_receipts'].values() if r['request_id'] == 'CT-bad')
        evidence = stored['payload']['submission_check']
        draft = next(r for r in evidence['artifacts'] if r['path'].endswith('/output.json'))
        self.assertEqual(engine.store.read(draft['path'], first_head), bad)
        self.assertEqual(hashlib.sha256(bad).hexdigest(), draft['sha256'])
        # Restart/replay reads the original receipt even after local bytes change.
        scene.sim.restart()
        engine = scene.engine
        (scene.workspace / 'draft.json').write_bytes(b'{changed local bytes')
        replay = engine._publish_control_request(request)
        self.assertEqual(replay['state'], 'rejected')
        self.assertEqual(engine.head, first_head)
        self.assertEqual(replay['result'], rejected['result'])
        # Optional local history is neither authority nor a submission prerequisite.
        (scene.workspace / 'checks').mkdir(exist_ok=True)
        (scene.workspace / 'checks/broken.json').write_bytes(b'{broken optional history')
        _, accepted = submit(scene, 'CT-good', canonical_json(scene.output))
        self.assertEqual(accepted['state'], 'accepted', accepted)
        final = engine._submission_check_summary(engine.head, engine.runtime)
        self.assertEqual(final['status'], 'verified', final)
        self.assertEqual(final['seal_count'], base['seal_count'] + 2)
        self.assertEqual(final['unresolved'], [])
        self.assertEqual(sum(final['rule_failure_counts'].values()), sum(first['rule_failure_counts'].values()))
        self.assertEqual(engine.runtime['executions']['EX-history']['status'], 'stopping')
        _, _, earlier = engine.store.load(first_head)
        self.assertEqual(engine._submission_check_summary(first_head, earlier), first)
        replay = engine._publish_control_request({**scene.binding, 'request_id': 'CT-good',
            'kind': 'submit_intent', 'payload': {'draft_path': 'draft.json'}})
        self.assertEqual(replay['state'], 'accepted')
        self.assertEqual(engine._submission_check_summary(engine.head, engine.runtime)['seal_count'], base['seal_count'] + 2)
        missing = deepcopy(engine.runtime)
        missing['events'] = [r for r in missing['events'] if r['kind'] != 'submission_checked']
        self.assertEqual(engine._submission_check_summary(engine.head, missing)['status'], 'incomplete')
        with self.assertRaisesRegex(ValueError, 'immutable'):
            engine.store._store.publish(engine.head, {draft['path']: b'tampered'})
        # This process already matched the draft, so it does not compare those bytes again
        # (이음새-정본.md §3). A process without that memo compares them and rejects changed bytes:
        # the memo is keyed by the repository's Git directory, so a copy of the repository at
        # another path is a repository this process never matched; there the draft bytes changed.
        copy = scene.sim.root / 'repository-unmatched'
        shutil.copytree(scene.sim.repository, copy)
        objects = scene.sim.ports.git_backend.objects
        objects[str((copy / '.git').absolute())] = dict(objects[str((scene.sim.repository / '.git').absolute())])
        unmatched = ResearchEngine(copy, scene.sim.instance_id, ports=scene.sim.ports, codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id)
        tampered = damage(unmatched.store, draft['path'], b'tampered')
        self.assertEqual(unmatched._submission_check_summary(tampered, engine.runtime)['status'], 'incomplete')
        # The same change on the matched repository is not compared again, as the comment above says.
        self.assertEqual(engine._submission_check_summary(damage(engine.store, draft['path'], b'tampered'),
                                                          engine.runtime)['status'], 'verified')


class WaitOwnershipTests(unittest.TestCase):
    def test_resolved_publication_and_impact_waits_are_removed(self):
        """The legacy scene, on the real receiver: the wait this sealed response discharges exists before its receipt."""
        for kind in ('submission_publication', 'impact_review'):
            with self.subTest(kind=kind):
                scene = history()
                _, accepted = submit(scene, 'CT-' + kind, canonical_json(scene.output))
                self.assertEqual(accepted['state'], 'accepted', accepted)
                scene.engine.runtime.setdefault('waiting_actions', {})[scene.action['id']] = {
                    'action': deepcopy(scene.action), 'kind': kind, 'execution_id': 'EX-history', 'reason': 'pending'}
                received = receive(scene)
                self.assertEqual(received['status'], 'accepted', received['issues'])
                self.assertNotIn(scene.action['id'], scene.engine.runtime['waiting_actions'])

    def test_a_publication_wait_left_by_a_failed_compare_and_swap_ends_with_the_retried_receipt(self):
        """Wiring: the owner's retry receives the sealed response again and the receipt removes the wait it discharges."""
        scene = history()
        _, accepted = submit(scene, 'CT-publication', canonical_json(scene.output))
        self.assertEqual(accepted['state'], 'accepted', accepted)
        with held_ref(scene.sim):
            returned = receive(scene)
        self.assertEqual([row['next_owner'] for row in returned['bundles']], ['engine'])
        wait = scene.engine.runtime['waiting_actions'][scene.action['id']]
        self.assertEqual((wait['kind'], wait['execution_id'], wait['next_owner']),
                         ('submission_publication', 'EX-history', 'engine'))
        scene.engine._save()
        with ObservedCalls(receive=ResearchEngine._receive_submission) as calls:
            scene.engine._retry_submission_publications()
        self.assertEqual(1, calls.count('receive'))
        self.assertNotIn(scene.action['id'], scene.engine.runtime['waiting_actions'])
        self.assertEqual(scene.engine.runtime['executions']['EX-history']['outcome'], 'output_accepted')


class TaskReceiptTests(unittest.TestCase):
    def test_task_receipt_occurs_once_after_the_complete_bundle_result(self):
        for owner in (None, 'engine'):
            with self.subTest(owner=owner):
                scene = history()
                _, accepted = submit(scene, 'CT-receipt', canonical_json(scene.output))
                self.assertEqual(accepted['state'], 'accepted', accepted)
                engine = scene.engine
                engine.runtime['queue'].clear()
                engine._save()
                calls = order(bundles=ResearchEngine._apply_submission_bundles,
                              receipt=ResearchEngine._record_task_receipt)
                if owner is None:
                    with calls:
                        receive(scene)
                else:
                    # The publication's compare-and-swap fails: the bundle returns to the engine.
                    with held_ref(scene.sim), calls:
                        receive(scene)
                execution = scene.engine.runtime['executions']['EX-history']
                # The receipt starts after the bundle application returned: no application frame encloses it.
                self.assertEqual(calls.order, [('bundles', ()), ('receipt', ())] if owner is None
                                 else [('bundles', ())])
                self.assertEqual(execution['status'], 'ended' if owner is None else 'stopping')
                if owner:
                    self.assertEqual(scene.engine.runtime['queue'], [])
                    self.assertEqual(scene.engine.runtime['waiting_actions'][scene.action['id']]['next_owner'],
                                     'engine')


class SealedRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.scene = history()

    def test_stopped_provider_recovers_the_frozen_submission_without_reading_original(self):
        scene = self.scene
        _, accepted = submit(scene, 'CT-frozen', canonical_json(scene.output))
        self.assertEqual(accepted['state'], 'accepted', accepted)
        (scene.workspace / 'draft.json').write_bytes(canonical_json({"changed": True}))
        execution = scene.engine.runtime['executions']['EX-history']
        recovered = scene.engine._collect_submitted_result(execution, {"status": "stopped", "usage": {}},
                                                           scene.context, scene.schema, scene.workspace)
        self.assertEqual("completed", recovered["status"])
        self.assertEqual("sealed_submission", recovered["collection"])
        self.assertEqual(scene.output, recovered["output"])

    def test_result_file_recovery_uses_the_receipt_snapshot_not_live_workspace(self):
        scene = self.scene
        research = scene.workspace / "research.txt"
        research.write_bytes(b"accepted bytes")
        _, accepted = submit(scene, 'CT-files', canonical_json(scene.output))
        self.assertEqual(accepted['state'], 'accepted', accepted)
        research.write_bytes(b"later mutation")
        execution = scene.engine.runtime['executions']['EX-history']
        self.assertIn('research.txt', [row['path'] for row in execution['submission_intent']['file_refs']])
        recovered = scene.engine._sealed_submission_files(execution)
        self.assertEqual(b"accepted bytes", recovered["files"]["research.txt"])


class PreviewEntryTests(unittest.TestCase):
    def test_real_preview_entry_accepts_questions_without_publishing(self):
        scene = history()
        engine = scene.engine
        execution = engine.runtime['executions']['EX-history']
        output = {**deepcopy(scene.output), 'questions': ['What should operations decide?']}
        seal_response(output, scene.context, scene.workspace)
        draft = scene.workspace / 'draft.json'
        draft.write_bytes(canonical_json(output))
        (scene.workspace / 'activity-extensions.json').write_bytes(b'{"knowledge_changes": []}')
        before, head = canonical_json(engine.runtime), engine.head
        issued = {'runtime/artifacts/BA-history-input/input/submission/context.json',
                  'runtime/artifacts/BA-history-input/schema.json'}
        with ObservedCalls(validate=ResearchRepository.validate_candidate, read=ResearchRepository.read) as calls:
            preview = engine._preview_submission(execution, {'draft_path': 'draft.json'})
            self.assertTrue(preview['passed'], preview['issues'])
            self.assertEqual(canonical_json(engine.runtime), before)
            self.assertEqual(engine.head, head)
            self.assertNotIn('artifact_bundle', engine.runtime['executions']['EX-history'])
            self.assertEqual(calls.count('validate'), 1)
            self.assertFalse(engine.runtime['question_links'])
            # The preview reads its issued input from Git and nothing else, so no artifact it sealed is read back.
            self.assertEqual({row['path'] for row in calls.captured('read')}, issued)
            invalid = {**output, 'used_sources': ['TK-not-in-input']}
            seal_response(invalid, scene.context, scene.workspace)
            draft.write_bytes(canonical_json(invalid))
            rejected = engine._preview_submission(execution, {'draft_path': 'draft.json'})
            self.assertFalse(rejected['passed'])
            self.assertEqual(canonical_json(engine.runtime), before)
            self.assertEqual(calls.count('validate'), 1)
            self.assertEqual({row['path'] for row in calls.captured('read')}, issued)


class CentralSubmissionEvidence(unittest.TestCase):
    def test_unsealed_runner_output_is_preserved_but_cannot_be_integrated(self):
        from do_math.execution_lifecycle import transition_execution
        scene = history()
        engine = scene.engine
        engine.instance['config']['max_output_repairs'] = 1
        execution = engine.runtime['executions']['EX-history']
        transition_execution(execution, 'stopping', at=engine.ports.clock.now())
        output = {"summary": "preserved exact draft"}
        (scene.workspace / "draft.json").write_bytes(json.dumps(output, indent=4).encode())
        with ObservedCalls(bundles=ResearchEngine._apply_submission_bundles, save=ResearchEngine._save) as calls:
            result = engine._receive_submission(scene.action, {"output": output}, "EX-history", scene.context,
                                                scene.schema, scene.workspace)
        self.assertEqual(result["status"], "returned")
        (arguments,) = calls.captured('bundles')
        self.assertTrue(any(issue["rule_id"] == "submission.sealed_candidate" for issue in arguments['issues']))
        saved = calls.captured('save')[0]['artifacts']
        self.assertTrue(any(path.endswith("/output.json") for path in saved))
        reference = engine.runtime['executions']['EX-history']['submitted_output_ref']
        self.assertEqual(engine.store.read(reference, engine.head), canonical_json(output))

    def test_retry_receives_prior_accepted_response_across_multiple_attempts(self):
        engine = Sim.activated().engine
        action = {"role": "research_work"}
        engine.runtime["executions"].update({"EX-one": {"action": deepcopy(action)},
            "EX-two": {"action": {**action, "continuation_of": "EX-one"}}})
        receipt = {"id": "IN-report", "execution_id": "EX-one", "response_sha256": "a" * 64}
        engine.runtime["integrations"] = {receipt["id"]: receipt}
        issue = integration.issue("integration.candidate", "output", "repair this")
        context = {}
        engine._submission_repair_context(context, {**action, "continuation_of": "EX-two", "repair": {"issues": [issue]}})
        self.assertEqual(context["accepted_response"], {"integration_id": "IN-report", "response_sha256": "a" * 64})
        self.assertEqual(context["submission_failures"], [issue])
        self.assertEqual(context["accepted_integration_ids"], ["IN-report"])


def titles(engine):
    return {row['title'] for row in engine.instance['knowledge'].values()}


class PartialCaptureGitTests(unittest.TestCase):
    def setUp(self):
        self.scene = research()
        # The independent A record can be imported without the returned report's
        # task disposition; this scene intentionally tests the capture seam.
        output = self.scene.output
        output['integration_bundles'][0]['members'].remove('output')
        output['integration_bundles'][1]['members'].append('output')
        output['knowledge'][1]['dependencies'] = ['KN-not-supplied']

    def test_early_submission_preview_reload_and_partial_application(self):
        scene = self.scene
        engine = scene.engine
        execution = engine.runtime['executions']['EX-partial']
        (scene.workspace / 'draft.json').write_bytes(canonical_json(scene.output))
        head = engine.head
        preview = engine._preview_submission(execution, {'draft_path': 'draft.json'})
        self.assertEqual(engine.head, head)
        self.assertEqual([row['status'] for row in preview['bundles']], ['preview_passed', 'returned'], preview)
        _, receipt = submit(scene, 'CT-partial', canonical_json(scene.output))
        self.assertEqual(receipt['state'], 'accepted', receipt)
        scene.sim.restart()
        engine = scene.engine
        execution = engine.runtime['executions']['EX-partial']
        sealed = submission.read_sealed_submission(execution, engine.head, engine.store.read)
        self.assertFalse(sealed['check']['passed'])
        self.assertEqual(engine._submission_check_summary(engine.head, engine.runtime)['status'], 'verified')
        applied = engine._apply_submission_bundles(execution['action'], sealed['output'], sealed['extensions'],
            execution['id'], scene.context, sealed['check']['issues'])
        self.assertEqual([row['status'] for row in applied['bundles']], ['accepted', 'returned'], applied['issues'])
        repeated = engine._apply_submission_bundles(execution['action'], sealed['output'], sealed['extensions'],
            execution['id'], scene.context, sealed['check']['issues'])
        self.assertEqual(repeated['bundles'][0]['status'], 'already_accepted')

    def test_native_final_reaches_the_same_partial_candidate(self):
        from support.submission_receiver import native_result
        scene = self.scene
        engine = scene.engine
        execution = engine.runtime['executions']['EX-partial']
        result = native_result(scene.sim, execution, scene.context, canonical_json(scene.output), scene.workspace)
        captured = engine._collect_submitted_result(execution, result, scene.context, scene.schema, scene.workspace)
        self.assertEqual(captured['collection'], 'sealed_submission', captured)
        self.assertNotIn('rejected_submission', captured)
        received = engine._receive_submission(execution['action'], captured, execution['id'], scene.context,
                                              scene.schema, scene.workspace, preserved=True)
        self.assertEqual([row['status'] for row in received['bundles']], ['accepted', 'returned'], received['issues'])


class BundleConnections(unittest.TestCase):
    def test_independent_commit_survives_later_bundle_failure_and_retry(self):
        """The second bundle's record names an undefined kind, so the storage contract rejects its candidate."""
        scene = research()
        engine = scene.engine
        output = scene.output
        output['knowledge'][1]['kind'] = 'undefined_kind'
        before = set(engine.instance['knowledge'])
        with ObservedCalls(publish=ResearchRepository.save_validated,
                           receipt=ResearchEngine._record_task_receipt) as calls:
            result = engine._apply_submission_bundles(scene.action, output, {}, 'EX-partial', scene.context, [])
            self.assertEqual(result['retry_bundle_ids'], ['IN-B'])
            # Exactly one record is new and it is A (the legacy accepted titles were exactly ['valid']).
            self.assertEqual([engine.instance['knowledge'][kid]['title'] for kid in set(engine.instance['knowledge']) - before],
                             ['A'])
            self.assertEqual(calls.count('publish'), 1)
            self.assertEqual(calls.count('receipt'), 0)
            _, _, published = engine.store.load()
            self.assertIn('IN-A', published['integrations'])
            self.assertNotIn('IN-B', published['integrations'])
            result = engine._apply_submission_bundles(scene.action, output, {}, 'EX-partial', scene.context, [])
            self.assertEqual(result['bundles'][0]['status'], 'already_accepted')
            self.assertEqual([engine.instance['knowledge'][kid]['title'] for kid in set(engine.instance['knowledge']) - before],
                             ['A'])
            self.assertEqual(calls.count('publish'), 1)


class ContinuationConnections(unittest.TestCase):
    def test_same_domain_callback_is_available_to_preview_without_publication(self):
        scene = research()
        engine = scene.engine
        bundle = next(row for row in integration.split_bundles(scene.output, {}, scene.context)
                      if row['integration_id'] == 'IN-A')
        before, head = canonical_json({'instance': engine.instance, 'runtime': engine.runtime}), engine.head
        instance, runtime = deepcopy(engine.instance), deepcopy(engine.runtime)
        known = set(instance['knowledge'])
        with ObservedCalls(save=ResearchEngine._save, receipt=ResearchEngine._record_task_receipt,
                           apply=ResearchEngine._apply) as calls:
            engine._apply_bundle_candidate(instance, runtime, bundle, action=scene.action, execution_id='EX-partial',
                                           extensions={})
        self.assertEqual(canonical_json({'instance': engine.instance, 'runtime': engine.runtime}), before)
        self.assertEqual(engine.head, head)
        # The domain application runs once, and its effect lands on the caller's copies only:
        # the one new record of the copy is A, and the engine has none.
        self.assertEqual(calls.count('apply'), 1)
        self.assertEqual([instance['knowledge'][kid]['title'] for kid in set(instance['knowledge']) - known], ['A'])
        self.assertNotIn('A', titles(engine))
        self.assertEqual(calls.count('save'), 0)
        self.assertEqual(calls.count('receipt'), 0)

    def test_bundle_requires_live_prior_hash_and_review_only_for_impact_beyond_the_closure(self):
        engine = Sim.activated().engine
        engine.instance, engine.runtime, kid = knowledge_io.import_candidate(engine.instance, engine.runtime,
            {"kind": "theorem", "title": "T", "statement": "True", "summary": "True", "explanation": "Proof",
             "lean_code": "theorem t : True := by trivial", "declaration_names": ["t"], "dependencies": []},
            source_ref="EX-author", actor_ref="EX-author", clock=engine.ports.clock)
        engine.runtime["tasks"]["TK-dependent"] = {"id": "TK-dependent", "dependencies": [kid]}
        engine.runtime["tasks"]["TK-other"] = {"id": "TK-other", "dependencies": []}
        change = {"id": kid, "changes": {"summary": "New summary"}, "reason": "clarification",
                  "impact_set": ["TK-dependent"]}
        bundle = {"integration_id": "IN-revision", "output": {}, "owns_response": False,
                  "extensions": {"knowledge_changes": [change]}, "impact_set": ["TK-dependent"],
                  "previous_hashes": {kid: knowledge.content_hash(engine.instance["knowledge"][kid])},
                  "members": ["activity-extensions.json/knowledge_changes/0"], "payload_sha256": "a" * 64}
        action = {"id": "AC-revise", "role": "research_work"}
        engine.runtime["executions"]["EX-author"] = {"id": "EX-author", "role": "research_work",
                                                     "input_snapshot": engine.head}
        engine._validate_bundle_impacts(engine.instance, engine.runtime, bundle, action=action, execution_id="EX-author")
        omitted = deepcopy(bundle)
        omitted["impact_set"] = []
        # The computed closure is applied whatever was declared, so an omission needs no review.
        self.assertEqual(engine._validate_bundle_impacts(engine.instance, engine.runtime, omitted, action=action,
                                                         execution_id="EX-author"), {})
        beyond = deepcopy(bundle)
        beyond["impact_set"] = ["TK-dependent", "TK-other"]
        with self.assertRaisesRegex(integration.ImpactReviewRequired, "^designated independent impact review required$"):
            engine._validate_bundle_impacts(engine.instance, engine.runtime, beyond, action=action,
                                            execution_id="EX-author")
        engine.instance["knowledge"][kid]["title"] = "Changed after input"
        with self.assertRaisesRegex(ValueError, re.escape("bundle previous semantic hash changed: " + kid)):
            engine._validate_bundle_impacts(engine.instance, engine.runtime, bundle, action=action,
                                            execution_id="EX-author")


class KnowledgeConnections(unittest.TestCase):
    def work(self, task):
        """A Sim engine holding ``task`` and the ended research execution ``EX-work``, two reviewers configured."""
        engine = Sim.activated().engine
        engine.instance["config"]["reviewers"] = 2
        engine.runtime["tasks"]["TK-work"] = task
        engine.runtime["executions"]["EX-work"] = {"id": "EX-work", "status": "ended", "extensions": {}}
        return engine

    def test_research_receipt_creates_separate_knowledge_authorities(self):
        engine = self.work({"id": "TK-work", "status": "active", "results": []})
        output = {"summary": "result", "used_sources": [], "questions": [], "report": "Established a result",
                  "outcome": "submitted", "remaining_work": [], "checkpoint": "done", "relations": [],
                  "knowledge": [{"kind": "theorem", "title": "T", "statement": "True", "explanation": "By construction",
                                 "summary": "True holds", "lean_code": "theorem t : True := by trivial",
                                 "declaration_names": ["t"], "dependencies": []}]}
        before = set(engine.instance["knowledge"])
        engine._apply({"id": "AC-work", "role": "research_work", "target": "TK-work"}, output, "EX-work")
        (kid,) = set(engine.instance["knowledge"]) - before
        record = engine.instance["knowledge"][kid]
        self.assertNotIn("lean_code", record)
        self.assertNotIn("formal", record)
        self.assertNotIn("reviews", record)
        self.assertIn(record["formal_result_id"], engine.instance["formal_results"])
        self.assertIn(record["exposition_id"], engine.instance["expositions"])
        self.assertEqual(len(engine.runtime["tasks"]["TK-work"]["results"]), 1)
        stored = engine.runtime['tasks']['TK-work']['results'][0]
        self.assertEqual(stored['report'], output['report'])
        for excluded in ('knowledge', 'relations', 'integration_bundles'):
            self.assertNotIn(excluded, stored)
        self.assertEqual(stored['output_files'], [])
        self.assertEqual(engine.runtime["tasks"]["TK-work"]["status"], "waiting")

    def test_independent_bundle_does_not_repeat_the_task_report(self):
        engine = self.work({"id": "TK-work", "status": "waiting", "results": [{"report": "already accepted"}]})
        output = {"report": "already accepted", "outcome": "submitted", "remaining_work": [],
                  "summary": "result", "questions": [], "knowledge": [], "relations": []}
        engine._apply({"id": "AC-work", "role": "research_work", "target": "TK-work"}, output, "EX-work",
                      owns_response=False)
        self.assertEqual(engine.runtime["tasks"]["TK-work"]["results"], [{"report": "already accepted"}])


class ReceiptPreservationTests(unittest.TestCase):
    def test_accepted_batch_opens_one_plan_and_preserves_all_evidence(self):
        engine = Sim.activated().engine
        engine.instance = knowledge_io.ensure_ontology(engine.instance)
        engine.runtime['tasks']['TK'] = {'id': 'TK', 'results': [], 'status': 'active'}
        engine.runtime['executions']['EX'] = {'id': 'EX', 'role': 'research_work', 'status': 'running',
                                              'extensions': {}}
        engine.runtime['queue'] = []
        self.assertEqual(engine.instance['knowledge'], {})
        start = deepcopy((engine.instance, engine.runtime))
        for count in (3, 1, 0):
            with self.subTest(count=count):
                engine.instance, engine.runtime = deepcopy(start)
                output = {'summary': 'Report', 'questions': [], 'used_sources': [], 'outcome': 'partial',
                          'report': 'Actual report', 'remaining_work': ['Open obligation'], 'checkpoint': '',
                          'relations': [], 'knowledge': [knowledge_candidate(title='K' + str(i), lean_code='',
                                                                             declaration_names=[])
                                                         for i in range(count)]}
                engine._apply({'id': 'AC', 'role': 'research_work', 'target': 'TK'}, output, 'EX')
                stored = engine.runtime['tasks']['TK']['results']
                self.assertEqual(stored[0]['report'], output['report'])
                assert_result_documents(self, stored, Path(engine.instance['workspace']), engine,
                                        owner='results', task_id='TK')
                plans = [a for a in engine.runtime['queue'] if a['role'] == 'research_plan']
                self.assertEqual(len(plans), 1, plans)
                self.assertEqual(set(plans[0]['evidence_refs']), set(engine.instance['knowledge']))
                self.assertEqual(len(engine.instance['knowledge']), count)
                self.assertEqual(plans[0]['receipt_refs'], ['EX'])


if __name__ == "__main__":
    unittest.main()
