"""The engine's receipt of producer calls that end invalid, failed or superseded, on a Sim.

Each scene runs model calls through the worker (over the 2 s Sim budget); the
calls the owner stops while they run are in ``sim/test_submission_engine_calls.py``. The
legacy tests put ``CheckedRunner`` around a scripted runner on the synthetic
active state; here the owner runs on a restored Sim and the model double
answers (``support.submission_calls``): outputs are submitted with the workspace
tool, failures are provider CLIs that exit with an error, and what the legacy
runner did while its call was in flight runs in the call's hooks while the owner
takes its turns. Identity reviews start from ``support.review_sim.opened_sim``
(a theorem imported by control whose review the owner opened).
"""
import json
from copy import deepcopy
from pathlib import Path
import unittest

from do_math.canonical import canonical_json
from do_math.knowledge import assess_use, plan_impact, revision_roots
from support.purpose_answers import common
from support.engine_lifecycle import applied
from support.model import Answer
from support.review_sim import opened_sim
from support.sim import Sim, warm_template
from support.submission_calls import applied_now, configured_sim, failed, submission_model, submitted

NO_REPAIR = {'max_output_repairs': 0}


def setUpModule():
    warm_template()
    configured_sim(**NO_REPAIR)
    opened_sim()


def new_executions(sim, before):
    return [row for eid, row in sim.runtime['executions'].items() if eid not in before]


class ProducerCallTests(unittest.TestCase):
    def test_user_decision_from_sealed_operational_review_preserves_question_reference(self):
        from support.scheduling_parallel import ready_work_sim
        sim = ready_work_sim(1, max_output_repairs=0)
        sim.model.on('research_work').reply(failed('Preserved provider failure needs a user decision'))
        sim.run_until(lambda s: any(row.get('role') == 'operational_review' and row['status'] == 'ended'
                                   for row in s.runtime['executions'].values()), max_steps=12)
        review = next(row for row in sim.runtime['executions'].values() if row['role'] == 'operational_review')
        self.assertEqual(review['outcome'], 'output_accepted', review.get('error'))
        self.assertEqual(review['submission_receipt']['state'], 'accepted')
        check = json.loads(sim.engine.store.read(review['submission_intent']['check_ref'], sim.engine.head))
        self.assertEqual((check['passed'], check['issues']), (True, []))
        record = next(row for row in sim.runtime['operational_dispositions'].values()
                      if row['execution_id'] == review['id'])
        self.assertEqual((record['status'], record['disposition']['kind']), ('applied', 'user_decision'))
        question = next(row for row in sim.runtime['question_links'] if row['id'] == record['question_id'])
        self.assertEqual((question['owner'], question['origin_execution_id']), ('user', review['id']))
        self.assertEqual(question['origin_field'], 'output/disposition/question')
        published = deepcopy(sim.engine.store.load())
        sim.restart()
        self.assertEqual(sim.engine.store.load(), published)
        head, instance, runtime = published
        for reference, reason in (
                ('Q-missing', '^operational_dispositions references unknown record: Q-missing$'),
                (review['id'], '^operational_dispositions reference has wrong family: ' + review['id'] + '$')):
            with self.subTest(reference=reference):
                damaged = deepcopy(runtime)
                damaged['operational_dispositions'][record['id']]['question_id'] = reference
                original = deepcopy(damaged)
                with self.assertRaisesRegex(ValueError, reason):
                    sim.engine.store.save_with_state(head, instance, damaged)
                self.assertEqual(damaged, original)
                self.assertEqual(sim.engine.store.load(), published)

    def test_unsealed_invalid_runner_output_is_preserved_for_operational_review(self):
        sim = configured_sim(**NO_REPAIR)
        before = set(sim.runtime["executions"])
        model = submission_model(sim)
        # An empty output, sealed and submitted like the legacy runner's through CheckedRunner.
        model.on(sim.runtime['queue'][0]['role']).reply(submitted({}))
        sim.step()
        execution, = new_executions(sim, before)
        self.assertEqual(execution["outcome"], "execution_incomplete")
        self.assertEqual(execution["error_kind"], "output_schema")
        self.assertIn(execution["action"]["id"], sim.runtime["waiting_actions"])
        self.assertEqual(sim.runtime["waiting_actions"][execution["action"]["id"]]["kind"], "output_validation")
        self.assertTrue(any(a["role"] == "operational_review" and a.get("target") == execution["id"]
                            for a in sim.runtime["queue"]))
        self.assertFalse(any(a.get("repair") for a in sim.runtime["queue"]))

    def test_receiver_rejects_unknown_insight_kind_and_missing_evidence(self):
        cases = {'kind': ({"kind": "unregistered_kind"}, 'kind', 'insight kind must be active or proposed'),
                 'evidence': ({"evidence_ids": ["KN-missing"]}, 'evidence_ids',
                              'insight evidence must name existing input records')}
        for name, (changes, field, message) in cases.items():
            with self.subTest(changes=changes):
                sim = configured_sim(**NO_REPAIR)
                before = set(sim.runtime['executions'])
                output = {**common("Preserve a candidate."), "candidates": []}
                insight = {"kind": "question", "title": "Question", "statement": "What remains?",
                           "summary": "An open question.", "evidence_ids": [], **changes}
                model = submission_model(sim)
                model.on("research_preparation").reply(
                    submitted(output, extensions={"research_insights": [insight]}))
                drafts = []
                # The draft the model wrote and submitted: the sealed output with its bundle declaration.
                model.after("research_preparation",
                            lambda context, workspace: drafts.append((Path(workspace) / "output.json").read_bytes()))
                self.assertEqual(sim.runtime['queue'][0]['role'], 'research_preparation')
                sim.step()
                execution, = new_executions(sim, before)
                self.assertEqual(execution["outcome"], "execution_incomplete")
                self.assertEqual(sim.instance["knowledge"], {})
                # The central check rejected the submitted insight and preserved the submitted output with it.
                receipt, = [row for row in sim.runtime['control_receipts'].values()
                            if row.get('execution_id') == execution['id']]
                self.assertEqual(receipt['state'], 'rejected')
                engine = sim.engine
                check_ref = receipt['payload']['submission_check']['check_ref']
                issues = json.loads(engine.store.read(check_ref, engine.head))['issues']
                self.assertEqual([(row['path'], row['message']) for row in issues],
                                 [('activity-extensions.json/research_insights/0/' + field, message)])
                # The sealed draft sits beside its check (a workspace file of the same name is under files/).
                saved = check_ref.rsplit('/', 1)[0] + '/output.json'
                self.assertIn(saved, [row['path'] for row in receipt['payload']['submission_check']['artifacts']])
                raw = engine.store.read(saved, engine.head)
                # The preserved output is exactly the draft the model submitted, its seal's fields included
                # (the legacy runner's output after CheckedRunner sealed it in place) ...
                self.assertEqual(len(drafts), 1)
                self.assertEqual(raw, drafts[0])
                # ... and apart from the seal's bundle declaration and a preparation's regeneration time it is
                # the runner's output.
                stored = json.loads(raw)
                sealed = ('integration_bundles', 'regenerate_after')
                self.assertEqual({key: value for key, value in stored.items() if key not in sealed}, output)
                self.assertEqual(set(stored) - set(output), set(sealed))


class LiveReviewTests(unittest.TestCase):
    def test_live_review_validates_sidecar_before_applying_continue(self):
        """A live review opened by a running call's observations answers ``continue``; an unregistered insight blocks it.

        The legacy flow's research call streamed a message and a tool start, let
        the tool review window pass and ticked, so the owner's observation
        application opened the live review. The Jobs fake runs a worker to its end
        inside the Job's resume, so the stream is handed to the owner's
        ``_observe_running`` directly, as a runner delivers it: running research
        work published through the product's lifecycle functions
        (``support.provider_live.running_execution``), a tracker built from its
        adopted profile, the tool start, the Sim clock past the profile's tool
        review window, and the tick. The engine's own trigger then queues the live
        review, which runs through the worker. The valid case shows that this scene
        applies a valid ``continue``, so the invalid case is rejected for its sidecar.
        """
        from do_math.observations import ObservationTracker, tracker_config
        from support.observation_inputs import observation_rule
        from support.provider_live import batch, running_execution

        def proceed(out, context):
            return {**common('A checkpoint and a visible observation are available'), 'disposition': {
                'kind': 'continue', 'basis_refs': [context['action']['target']], 'next_owner': 'research_work',
                'reason': 'The visible checkpoint contains the fixture argument', 'next_review': None}}

        def unregistered(context, workspace):
            (Path(workspace) / 'activity-extensions.json').write_bytes(canonical_json({'research_insights': [{
                'kind': 'not_registered', 'title': 'Bad insight', 'statement': 'x', 'summary': 'x'}]}))
        for sidecar in ('unregistered', 'valid'):
            with self.subTest(sidecar=sidecar):
                sim = Sim.activated()
                sim.engine.runtime['queue'] = []
                sim.engine._save()
                workspace = running_execution(sim, 'EX-work', 'research_work', bind=True)
                # What the legacy worker wrote before it streamed: its argument and a checkpoint.
                (workspace / 'argument.txt').write_text('The domain is Nat; Nat.add_zero supplies the equality.',
                                                        encoding='utf-8')
                (workspace / 'checkpoint.json').write_bytes(canonical_json({
                    'current_claim': 'Adding zero leaves a natural number unchanged.', 'evidence_paths': ['argument.txt'],
                    'attempts': ['Reconstructed Nat.add_zero'], 'remaining_work': ['Write the final report'],
                    'next_step': 'Finish the explicit report', 'progress_state': 'working', 'counters': {'attempts': 1}}))
                profile = sim.instance['execution_profiles'][sim.instance['role_profile_refs']['research_work'][0]['id']]
                config = tracker_config(profile, initial_self_check_rules=[observation_rule()])
                tracker = ObservationTracker('EX-work', workspace, config, time_port=sim.clock)
                stream = workspace.parent / 'evidence' / 'stdout.jsonl'
                started = batch(sim, [
                    {'type': 'item.completed', 'item': {'type': 'agent_message', 'id': 'm1', 'text': 'The Nat domain is fixed.'}},
                    {'type': 'item.started', 'item': {'type': 'command_execution', 'id': 'observed-tool'}}], stream)
                sim.engine._observe_running('EX-work', tracker, started)
                self.assertEqual(sim.runtime['queue'], [], 'the review waits for the tool review window')
                sim.advance(config['tool_review_window_seconds'] + 1)
                sim.engine._observe_running('EX-work', tracker, batch(sim, [], stream, start=started.end_offset))
                opened, = sim.runtime['queue']
                self.assertEqual((opened['role'], opened['target'], opened['live']), ('operational_review', 'EX-work', True))
                self.assertEqual(sim.runtime['observations']['EX-work']['kind'], 'tool_review_due')
                self.assertEqual(opened['observation_refs'], sim.runtime['observations']['EX-work']['observation_refs'])
                model = submission_model(sim)
                if sidecar == 'unregistered':
                    model.before('operational_review', unregistered)
                model.on('operational_review').reply(Answer(proceed))
                sim.step()
                reviewed = next(x for x in sim.runtime['executions'].values()
                                if x['role'] == 'operational_review' and x['action'].get('live'))
                target = sim.runtime['executions'][reviewed['action']['target']]
                recorded = [row for row in sim.runtime.get('operational_dispositions', {}).values()
                            if row.get('execution_id') == reviewed['id']]
                if sidecar == 'valid':
                    self.assertEqual(reviewed['outcome'], 'output_accepted')
                    self.assertIn('operational_continuation', target)
                    self.assertEqual([row['disposition']['kind'] for row in recorded], ['continue'])
                    continue
                self.assertEqual(reviewed["outcome"], "execution_incomplete")
                self.assertNotIn("operational_continuation", target)
                self.assertEqual(recorded, [])
                receipt, = [row for row in sim.runtime['control_receipts'].values()
                            if row.get('execution_id') == reviewed['id']]
                issues = json.loads(sim.engine.store.read(receipt['payload']['submission_check']['check_ref'],
                                                          sim.engine.head))['issues']
                self.assertIn('activity-extensions.json/research_insights/0/kind', [row['path'] for row in issues])


class ReviewFailureTests(unittest.TestCase):
    def test_failed_contract_review_is_not_regenerated_while_waiting_for_diagnosis(self):
        sim = Sim.activated()
        sim.step()
        task_id = next(iter(sim.runtime["tasks"]))
        model = submission_model(sim)
        for role in ("task_contract_review", "research_plan", "research_preparation", "operational_review"):
            model.on(role).reply(failed("reviewer unavailable"))
        sim.step()
        self.assertEqual([call["role"] for call in model.calls], ["task_contract_review"])
        self.assertTrue(any(e["action"].get("target") == task_id for e in sim.runtime["waiting_actions"].values()))
        self.assertFalse(any(a["role"] == "task_contract_review" and a.get("target") == task_id
                             for a in sim.runtime["queue"]))

    def test_failed_identity_slot_is_not_regenerated_after_its_peer_finishes(self):
        sim = opened_sim()
        model = submission_model(sim)
        model.on("identity_review", slot="initial-0").reply(failed("reviewer unavailable"))

        def repair(out, context):
            return {**common("Preserved failure needs repair."), "disposition": {
                "kind": "repair", "basis_refs": [context["action"]["target"]], "next_owner": "operations",
                "reason": "Repair the execution environment.", "repair_target": "execution environment",
                "meaning_preserving": True, "verification": "Repeat the failed environment check"}}
        model.on("operational_review").reply(Answer(repair))
        sim.engine.run(max_steps=3)
        slots = [call["action"].get("slot") for call in model.calls if call["role"] == "identity_review"]
        self.assertIn("initial-1", slots, "the peer slot ran")
        self.assertFalse(any(a["role"] == "identity_review" and a.get("slot") == "initial-0" for a in sim.runtime["queue"]))
        self.assertTrue(any(e["action"].get("slot") == "initial-0" for e in sim.runtime["waiting_actions"].values()))

    def test_explicit_diagnosis_can_open_one_new_attempt_of_a_failed_action(self):
        sim = Sim.activated()
        sim.engine.runtime["queue"] = [{"id": "AC-failed", "role": "maintenance"}]
        sim.engine._save()
        model = submission_model(sim)
        model.on("maintenance").reply(failed("configuration failure"))

        def retry(out, context):
            return {**common("The explicit repair diagnosis is complete."), "disposition": {
                "kind": "retry", "basis_refs": [context["action"]["target"]], "next_owner": "engine",
                "reason": "The independent operator repaired the execution configuration and requested this diagnosis.",
                "scope": "One new attempt of the failed action",
                "replay_safety": "The failed local action produced no external effects"}}
        model.on("operational_review").reply(Answer(retry))
        sim.step()
        failed_id = next(eid for eid, e in sim.runtime['executions'].items() if e['action']['id'] == 'AC-failed')
        applied(sim, "request", origin="operator", config={"role": "operational_review", "target": failed_id},
                text="Inspect the repaired execution configuration before one new attempt.")
        diagnosis = next(a for a in sim.runtime['queue'] if a['role'] == 'operational_review' and a.get('target') == failed_id)
        sim.engine.runtime['queue'] = [diagnosis]
        sim.engine._save()
        sim.step()
        retries = [a for a in sim.runtime["queue"] if a["role"] == "maintenance"]
        self.assertEqual(len(retries), 1)
        self.assertEqual(retries[0]["id"], "AC-failed")
        self.assertEqual(retries[0]['continuation_of'], failed_id)

    # v5 task_scope decisions authorize named obligations; they do not directly
    # withdraw a live task. The task scope tests cover live and terminal withdrawal.

    def test_late_identity_result_is_preserved_without_retrying_a_superseded_slot(self):
        sim = opened_sim()
        self.assertEqual(sim.runtime["queue"][0]["role"], "identity_review")
        cid = sim.runtime["queue"][0]["review_cycle_id"]
        model = submission_model(sim)

        def revise(context, workspace):
            target = context["action"]["target"]
            roots = revision_roots(sim.engine.instance, target)
            applied_now(sim, "knowledge", config={"operation": "revise", "id": target,
                "changes": {'explanation': 'A replacement explanation of the same domain.'},
                'declared_impact': plan_impact(sim.engine.instance, sim.engine.runtime, roots, [])['computed_impact'],
                "reason": "Revise the sealed proposal."})
        # After the review's answer was sealed and received, as the legacy runner revised after its run.
        model.after("identity_review", revise)
        sim.step()
        self.assertFalse(any(a.get("review_cycle_id") == cid for a in sim.runtime["queue"]))
        review = next(e for e in sim.runtime["executions"].values() if e["role"] == "identity_review")
        self.assertNotEqual(review["outcome"], "output_accepted")
        engine = sim.engine
        self.assertIsNotNone(engine.store.read(review['submission_intent']['output_ref'], engine.head))
        self.assertTrue(json.loads(engine.store.read(review['submission_intent']['output_ref'], engine.head)))

    def test_private_insight_rechecks_its_own_basis_when_published_after_peer_review(self):
        sim = opened_sim()
        applied(sim, "knowledge", config={"operation": "import", "candidate": {
            "kind": "observation", "title": "Earlier computation", "statement": "The answer is one.",
            "explanation": "A bounded computation.", "summary": "One was computed.", "lean_code": ""}})
        kid = next(k for k, row in sim.instance["knowledge"].items() if row["title"] == "Earlier computation")
        sim.engine.runtime["queue"] = [a for a in sim.engine.runtime["queue"] if a["role"] == "identity_review"]
        sim.engine._save()
        model = submission_model(sim)

        def private_insight(context, workspace):
            action = context["action"]
            if action.get('stage') == 'initial' and action.get('slot') == 'initial-0':
                (Path(workspace) / 'activity-extensions.json').write_bytes(canonical_json({'research_insights': [{
                    'kind': 'question', 'title': 'Private followup', 'statement': 'What follows from the old computation?',
                    'summary': 'A possible followup.', 'evidence_ids': [kid]}]}))
        revised = []

        def revise(context, workspace):
            action = context["action"]
            if action.get('stage') == 'initial' and action.get('slot') == 'initial-1':
                roots = revision_roots(sim.engine.instance, kid)
                applied_now(sim, 'knowledge', config={'operation': 'revise', 'id': kid,
                    'changes': {'statement': 'The corrected answer is two.'},
                    'declared_impact': plan_impact(sim.engine.instance, sim.engine.runtime, roots, [])['computed_impact'],
                    'reason': 'Correct a computation.'})
                revised.append(kid)
        model.before("identity_review", private_insight)
        model.after("identity_review", revise)
        sim.run_until(lambda s: any(k["title"] == "Private followup" for k in s.instance["knowledge"].values()),
                      max_steps=45)
        self.assertEqual(revised, [kid])
        insight = next(k for k in sim.instance["knowledge"].values() if k["title"] == "Private followup")
        self.assertTrue(insight.get("use_suspended", False))
        self.assertEqual(insight["lifecycle"], "active")
        self.assertFalse(assess_use(insight, sim.instance)["valid"])
        self.assertEqual(insight["dependencies"], [kid])


if __name__ == "__main__":
    unittest.main()
