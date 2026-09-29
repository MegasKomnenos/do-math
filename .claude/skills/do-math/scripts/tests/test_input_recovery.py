"""Input-overflow recovery: the planner's profile choice and the public retry, in memory and against a temporary Git instance."""
from __future__ import annotations

import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from do_math import execution_profiles
from do_math.engine import ResearchEngine
from do_math.canonical import canonical_json
from runner_fixtures import ScriptedRunner, formal_ok
from research_fixtures import FixtureAdapter, bare_engine, cli_result, restore_template, run_cli
from state_fixtures import ACTIVE_CONFIG, active_instance, start_active_copy
from do_math import planning
from engine_fixtures import context_engine
from engine_fixtures import package
from unittest.mock import create_autospec
import hashlib
import tempfile


def apply_limit(root: Path, repository: Path, identifier: str, limit: int, request_id: str) -> ResearchEngine:
    """Configure ``max_input_bytes`` publicly and record the new profiles' capability evidence."""
    config = root / (request_id + ".json")
    config.write_bytes(canonical_json({"max_input_bytes": limit}))
    accepted = cli_result(root, "configure", "--repository", str(repository), "--instance", identifier,
                   "--config-file", str(config), "--request-id", request_id)
    if not accepted["accepted"]:
        raise AssertionError(accepted)
    engine = ResearchEngine(repository, identifier, runner=ScriptedRunner(), formal_verifier=formal_ok)
    engine.process_controls()
    evidence_store = engine.instance.setdefault("capability_evidence", {})
    for reference in engine.instance["role_profile_refs"]["maintenance"]:
        profile = execution_profiles.resolve_profile(engine.instance["execution_profiles"], reference)
        if profile["actor_kind"] != "ai":
            continue
        evidence = execution_profiles.capability_evidence(profile, FixtureAdapter().describe(),
            observed_at=engine.runtime["last_observed_utc"])
        evidence_store[evidence["id"]] = evidence
    engine._save()
    return engine


def overflowed_maintenance(root, shared):
    """``restore_template`` build: a public maintenance request held by its first input overflow.

    From the validated active state, a public ``configure`` sets ``max_input_bytes``
    to 1, a public ``request`` queues maintenance, and one engine step holds it.
    Returns the instance ID.
    """
    from unittest.mock import patch
    identifier = active_instance(root, shared, config=ACTIVE_CONFIG)
    repository = root / "repository"
    with patch("do_math.local_host.adapter_for", return_value=FixtureAdapter()):
        apply_limit(root, repository, identifier, 1, "UC-limit-small")
        requested = cli_result(root, "request", "--repository", str(repository), "--instance", identifier,
                        "--role", "maintenance", "--reason", "Check the installed recovery boundary",
                        "--request-id", "UC-maintenance")
        if not requested["accepted"]:
            raise AssertionError(requested)
        ResearchEngine(repository, identifier, runner=ScriptedRunner(), formal_verifier=formal_ok).run(max_steps=1)
    return identifier


class InputRecoveryPublicTests(unittest.TestCase):
    def setUp(self) -> None:
        start_active_copy(self)

    def overflowed(self) -> None:
        """Replace the copy with ``overflowed_maintenance``'s state."""
        self.root, self.identifier = restore_template(overflowed_maintenance)
        self.repo = self.root / "repository"

    def cli(self, *arguments: str) -> dict:
        return cli_result(self.root, *arguments)

    def instance_args(self, identifier: str) -> tuple[str, ...]:
        return "--repository", str(self.repo), "--instance", identifier

    def apply_limit(self, identifier: str, limit: int, request_id: str) -> ResearchEngine:
        return apply_limit(self.root, self.repo, identifier, limit, request_id)

    def test_public_retry_replays_refails_resolves_and_rejects_after_close(self):
        self.overflowed()
        identifier = self.identifier

        # The copied state is the first overflow: a public configure (limit 1),
        # a public maintenance request and one engine step.
        engine = ResearchEngine(self.repo, identifier, runner=ScriptedRunner(), formal_verifier=formal_ok)
        self.assertEqual(len(engine.runtime.get("input_overflows", [])), 1, {
            "status": engine.runtime["status"], "queue": engine.runtime["queue"],
            "waiting_actions": engine.runtime.get("waiting_actions", {}),
            "recent_history": engine.runtime["history"][-5:]})
        action_id, held = next(iter(engine.runtime["waiting_actions"].items()))
        first_question_id = held["question_id"]
        first_question = next(q for q in engine.runtime["question_links"] if q["id"] == first_question_id)
        self.assertEqual(first_question["origin_field"], "resolution_question/question")
        self.assertIsNotNone(first_question["origin_execution_id"])
        status = self.cli("status", *self.instance_args(identifier), "--json")
        public_question = next(q for q in status["question_links"] if q["id"] == first_question_id)
        self.assertEqual(public_question["text"], held["detail"]["resolution_question"]["question"])
        self.assertNotIn("source_status", public_question)

        first_retry = self.cli("request", *self.instance_args(identifier), "--retry-action", action_id,
                               "--request-id", "UC-retry-same-limit")
        replay = self.cli("request", *self.instance_args(identifier), "--retry-action", action_id,
                          "--request-id", "UC-retry-same-limit")
        self.assertTrue(first_retry["accepted"])
        self.assertTrue(replay["replayed"])
        engine = ResearchEngine(self.repo, identifier, runner=ScriptedRunner(), formal_verifier=formal_ok)
        engine.run(max_steps=1)
        self.assertEqual(len(engine.runtime["input_overflows"]), 2)
        self.assertEqual(sum(row.get("kind") == "input_overflow_retry_started"
                             and row.get("request_id") == "UC-retry-same-limit"
                             for row in engine.runtime["history"]), 1)
        self.assertTrue(any(row.get("kind") == "input_overflow_retry_failed"
                            for row in engine.runtime["history"]))
        self.assertEqual(next(q for q in engine.runtime["question_links"]
                              if q["id"] == first_question_id)["status"], "resolved")
        second_held = engine.runtime["waiting_actions"][action_id]
        second_question_id = second_held["question_id"]
        self.assertNotEqual(second_question_id, first_question_id)
        self.assertEqual(next(q for q in engine.runtime["question_links"]
                              if q["id"] == second_question_id)["status"], "open")

        engine = self.apply_limit(identifier, 3_000_000, "UC-limit-large")
        current_profiles = deepcopy(engine.instance["role_profile_refs"]["maintenance"])
        retry = self.cli("request", *self.instance_args(identifier), "--retry-action", action_id,
                         "--request-id", "UC-retry-large")
        self.assertTrue(retry["accepted"])
        engine = ResearchEngine(self.repo, identifier, runner=ScriptedRunner(), formal_verifier=formal_ok)
        engine.run(max_steps=1)
        self.assertNotIn(action_id, engine.runtime["waiting_actions"])
        self.assertEqual(next(q for q in engine.runtime["question_links"]
                              if q["id"] == second_question_id)["status"], "resolved")
        resolved = next(row for row in engine.runtime["history"]
                        if row.get("kind") == "input_overflow_retry_resolved")
        self.assertIn(resolved["profile_ref"], current_profiles)
        self.assertLessEqual(resolved["prompt_bytes"], resolved["limit_bytes"])
        self.assertEqual(len(engine.runtime["input_overflows"]), 2,
                         "successful admission must preserve both historical failures")

        self.cli("close", *self.instance_args(identifier), "--reason", "Boundary test complete")
        engine = ResearchEngine(self.repo, identifier, runner=ScriptedRunner(), formal_verifier=formal_ok)
        engine.process_controls()
        closed = run_cli("request", *self.instance_args(identifier), "--retry-action", action_id,
                         "--request-id", "UC-retry-closed", cwd=self.root)
        self.assertEqual(closed.returncode, 2, closed.stdout + closed.stderr)
        rejected = json.loads(closed.stdout)["error"]
        self.assertIn("closed/completed", rejected["message"])
        engine = ResearchEngine(self.repo, identifier, runner=ScriptedRunner(), formal_verifier=formal_ok)
        self.assertEqual(engine.runtime["status"], "closed")
        self.assertEqual(engine.runtime["queue"], [])

    def test_resolved_retry_marker_survives_provider_deferral_and_repreparation(self):
        self.overflowed()
        identifier = self.identifier

        engine = ResearchEngine(self.repo, identifier, runner=ScriptedRunner(), formal_verifier=formal_ok)
        action_id, held = next(iter(engine.runtime["waiting_actions"].items()))
        question_id = held["question_id"]

        self.apply_limit(identifier, 3_000_000, "UC-marker-limit-large")
        self.cli("request", *self.instance_args(identifier), "--retry-action", action_id,
                 "--request-id", "UC-marker-retry")
        engine = ResearchEngine(self.repo, identifier, runner=ScriptedRunner(), formal_verifier=formal_ok)

        def defer(action, *_args, **_kwargs):
            action["dispatch_wait"] = {"kind": "capacity", "provider": "test-double", "next_owner": "scheduler"}
            return False

        with patch.object(engine, "_provider_admit", side_effect=defer):
            engine.run(max_steps=1)
        first = next(q for q in engine.runtime["question_links"] if q["id"] == question_id)
        first_history = deepcopy(first["resolution_history"])
        first_resolution_ref = first["resolution_ref"]
        deferred = next(row for row in engine.runtime["queue"] if row["id"] == action_id)
        self.assertEqual(deferred["input_overflow_retry"]["state"], "resolved")

        engine = ResearchEngine(self.repo, identifier, runner=ScriptedRunner(), formal_verifier=formal_ok)
        engine.run(max_steps=1)
        after = next(q for q in engine.runtime["question_links"] if q["id"] == question_id)
        self.assertEqual(after["resolution_ref"], first_resolution_ref)
        self.assertEqual(after["resolution_history"], first_history)
        self.assertEqual(sum(row.get("kind") == "input_overflow_retry_resolved"
                             and row.get("request_id") == "UC-marker-retry"
                             for row in engine.runtime["history"]), 1)
        executions = [row for row in engine.runtime["executions"].values()
                      if row.get("action", {}).get("id") == action_id]
        self.assertTrue(any(row.get("outcome") == "start_failed"
                            and row.get("result_disposition", {}).get("kind") == "capacity"
                            and any(transition.get("reason") == "provider admission deferred"
                                    for transition in row.get("transitions", []))
                            for row in executions))
        self.assertTrue(any(row.get("outcome") == "output_accepted" for row in executions))


class InputRecoveryMarkerUnitTests(unittest.TestCase):
    def test_only_explicit_pending_retry_marker_is_active(self):
        pending = {"input_overflow_retry": {"question_id": "QU", "state": "pending"}}
        legacy_pending = {"input_overflow_retry": {"question_id": "QU"}}
        resolved = {"input_overflow_retry": {"question_id": "QU", "state": "resolved"}}
        failed = {"input_overflow_retry": {"question_id": "QU", "state": "failed"}}

        self.assertIsNotNone(ResearchEngine._pending_input_overflow_retry(pending))
        self.assertIsNone(ResearchEngine._pending_input_overflow_retry(legacy_pending))
        self.assertIsNone(ResearchEngine._pending_input_overflow_retry(resolved))
        self.assertIsNone(ResearchEngine._pending_input_overflow_retry(failed))

    def test_preexisting_user_resolution_is_preserved_when_retry_input_fits(self):
        prior_history = [{"resolution_ref": "DE-user", "affected_ids": ["AC-held"]}]
        engine = bare_engine(runtime={"question_links": [{
            "id": "QU-overflow", "status": "resolved", "resolution_ref": "DE-user",
            "unresolved_target_ids": [], "resolution_history": deepcopy(prior_history)}]})

        disposition = engine._resolve_input_overflow_question("QU-overflow", execution_id="EX-retry",
            kind="input_overflow_retry_resolved", evidence={"action_id": "AC-held"})

        question = engine.runtime["question_links"][0]
        self.assertEqual(disposition, "already_resolved")
        self.assertEqual(question["resolution_ref"], "DE-user")
        self.assertEqual(question["resolution_history"], prior_history)


class OverflowConnections(unittest.TestCase):
    def fixture(self):
        from do_math import activities, execution_profiles
        from do_math.engine import ResearchEngine
        from record_fixtures import approved_task, approve_task
        task, instance, runtime = approved_task()
        engine = context_engine(instance, runtime)
        config = engine.instance['config']
        profiles = execution_profiles.build_profiles(config)
        engine.store.read.return_value = b'source'
        engine.instance['sources'][0]['sha256'] = hashlib.sha256(b'source').hexdigest()
        engine.instance.update(profiles)
        small = execution_profiles.resolve_profile(profiles['execution_profiles'], profiles['role_profile_refs']['research_work'][0])
        large = deepcopy(small)
        large['input']['max_input_bytes'] *= 2
        large = execution_profiles.seal_profile(large)
        engine.instance['execution_profiles'][large['id']] = large
        task['profile_refs'] = [execution_profiles.profile_ref(small), execution_profiles.profile_ref(large)]
        task['status'] = 'active'
        engine.runtime['tasks'][task['id']] = task
        approve_task(task, engine.instance, engine.runtime)
        action = {'id': 'AC-held', 'role': 'research_work', 'target': task['id'],
            'owner_activity_id': 'AY-held', 'grant_id': 'GR-1',
            'selected_contract_sha256': planning.contract_hash(task), 'profile_ref': execution_profiles.profile_ref(small),
            'model_assessment': {'difficulty': 'low', 'importance': 'low', 'reason': 'Bounded work'}}
        activities.open_activity(engine.runtime, activity_id='AY-held', activity_kind='research_work',
            owner_ref='AC-held', input_refs=[task['id']], opened_at='2026-09-23T00:00:00+00:00')
        activities.wait_for(engine.runtime, 'AY-held', reason='input_overflow',
            condition={'action_ids': ['AC-held']}, next_owner='research_plan', at='2026-09-23T00:00:00+00:00')
        engine.runtime['waiting_actions'] = {'AC-held': {'kind': 'input_overflow', 'action': action,
            'question_id': 'QU-held', 'next_owner': 'research_plan', 'detail': {
                'allowed_profile_candidates': [large['id']], 'cause': 'required_role_input',
                'packed_bytes': small['input']['max_input_bytes'] + 10}}}
        engine.instance['conversation_loss_policy'] = 'continue_authorized'
        engine._require_action_clock = create_autospec(engine._require_action_clock,
                                                       side_effect=lambda: '2026-09-23T00:00:00+00:00')
        engine._execution_profile = ResearchEngine._execution_profile.__get__(engine)
        return engine, execution_profiles.profile_ref(large)

    def test_overflow_choices_are_supplied_without_changing_ready_population(self):
        engine, reference = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            fitted, fixed = package(engine, Path(directory))
        self.assertEqual(fixed['ready_task_ids'], [])
        item = fitted['context']['input_overflow_requests'][0]
        self.assertEqual(item['action_id'], 'AC-held')
        self.assertEqual(item['owner_activity_id'], 'AY-held')
        self.assertEqual(item['allowed_profile_refs'], [reference])

    def test_planner_extension_accepts_exact_choice_and_requeues_same_obligation(self):
        from do_math import submission
        import jsonschema
        engine, reference = self.fixture()
        choice = {'action_id': 'AC-held', 'profile_ref': reference, 'reason': 'Required evidence fits'}
        extension = {'input_overflow_resolutions': [choice]}
        jsonschema.validate(extension, submission.extension_schema({'role': 'research_plan'}))
        with tempfile.TemporaryDirectory() as directory:
            _, fixed = package(engine, Path(directory))
        engine._apply_input_overflow_resolutions([choice], fixed, 'EX-plan')
        action = next(a for a in engine.runtime['queue'] if a['id'] == 'AC-held')
        self.assertEqual(action['owner_activity_id'], 'AY-held')
        self.assertEqual(action['profile_ref'], reference)
        self.assertEqual(action['model_assessment']['difficulty'], 'low')
        self.assertEqual(action['input_overflow_retry']['request_id'], 'EX-plan')
        self.assertEqual(action['input_overflow_retry']['state'], 'pending')
        self.assertNotIn('AC-held', engine.runtime['waiting_actions'])

    def test_stale_contract_or_unoffered_profile_cannot_release_wait(self):
        for mutation in ('contract', 'profile', 'question', 'review'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                engine, reference = self.fixture()
                _, fixed = package(engine, Path(directory))
                choice = {'action_id': 'AC-held', 'profile_ref': reference, 'reason': 'Fits'}
                if mutation == 'contract':
                    engine.runtime['tasks']['TK-1']['revision'] += 1
                elif mutation == 'profile':
                    choice['profile_ref'] = engine.instance['role_profile_refs']['research_plan'][0]
                elif mutation == 'question':
                    engine.runtime['waiting_actions']['AC-held']['question_id'] = 'QU-new-failure'
                else:
                    engine.runtime['waiting_actions']['AC-held']['action']['role'] = 'identity_review'
                with self.assertRaises(ValueError):
                    engine._apply_input_overflow_resolutions([choice], fixed, 'EX-plan')
                self.assertIn('AC-held', engine.runtime['waiting_actions'])

    def test_shared_submission_check_rejects_duplicate_and_unoffered_choices(self):
        from do_math import contracts, submission
        from do_math.canonical import canonical_json
        from runner_fixtures import common
        from research_fixtures import seal_response
        engine, reference = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, fixed = package(engine, root)
            choice = {'action_id': 'AC-held', 'profile_ref': reference, 'reason': 'Fits required evidence'}
            for mode in ('valid', 'duplicate', 'profile', 'unknown'):
                row = deepcopy(choice)
                if mode == 'profile': row['profile_ref'] = engine.instance['role_profile_refs']['research_plan'][0]
                if mode == 'unknown': row['action_id'] = 'AC-unknown'
                extensions = {'input_overflow_resolutions': [row, row] if mode == 'duplicate' else [row]}
                (root / 'activity-extensions.json').write_bytes(canonical_json(extensions))
                output = common('research_plan')
                seal_response(output, fixed, root)
                issues = submission.payload_issues(output, contracts.schema_for('research_plan'), fixed, extensions, root)
                self.assertEqual(bool(issues), mode != 'valid', (mode, issues))

    def test_same_integration_receipt_prevents_duplicate_retry(self):
        from do_math import integration
        from runner_fixtures import common
        engine, reference = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            _, fixed = package(engine, Path(directory))
        extension = {'input_overflow_resolutions': [{'action_id': 'AC-held', 'profile_ref': reference, 'reason': 'Fits'}]}
        calls = []
        def apply(instance, runtime, bundle):
            calls.append(bundle['integration_id'])
            engine.instance, engine.runtime = instance, runtime
            engine._apply_input_overflow_resolutions(bundle['extensions']['input_overflow_resolutions'], fixed, 'EX-plan')
        callbacks = {'apply_bundle': apply, 'validate_candidate': lambda *args: None,
                     'validate_current': lambda *args: None, 'publish': lambda *args: None}
        first = integration.apply_bundles(engine.instance, engine.runtime, common('research_plan'), extension, fixed,
                                         execution_id='EX-plan', **callbacks)
        self.assertEqual(first['status'], 'accepted', first['issues'])
        second = integration.apply_bundles(first['instance'], first['runtime'], common('research_plan'), extension, fixed,
                                          execution_id='EX-plan', **callbacks)
        self.assertEqual(second['bundles'][0]['status'], 'already_accepted', second['issues'])
        self.assertEqual(len(calls), 1)
        self.assertEqual(len([a for a in second['runtime']['queue'] if a['id'] == 'AC-held']), 1)


class OverflowGitConnection(unittest.TestCase):
    def test_plan_choice_repackages_original_work_and_reaches_runner(self):
        from state_fixtures import start_active_copy
        from do_math.engine import ResearchEngine
        from do_math import execution_profiles
        from do_math.canonical import canonical_json
        from record_fixtures import task_contract as task_fixture, approve_task
        from runner_fixtures import common, context_from
        from research_fixtures import local_job_runner, producer_result
        start_active_copy(self)
        calls = []
        class Runner:
            @local_job_runner
            def run(self, **arguments):
                context = context_from(arguments['prompt'])
                calls.append(deepcopy(context['action']))
                role = context['action']['role']
                output = common(role)
                if role == 'research_plan':
                    row = context['input_overflow_requests'][0]
                    extension = {'input_overflow_resolutions': [{'action_id': row['action_id'],
                        'profile_ref': row['allowed_profile_refs'][0], 'reason': 'The complete input fits this allowed profile'}]}
                    (arguments['workspace'] / 'activity-extensions.json').write_bytes(canonical_json(extension))
                elif role == 'research_work':
                    output.update(outcome='submitted', report='Read the complete assigned input and preserved the result.')
                else:
                    raise AssertionError('Unexpected role: ' + role)
                arguments['on_started']({'fixture': 'overflow response'})
                return producer_result({'status': 'completed', 'output': output, 'usage': {}}, arguments)
        engine = ResearchEngine(self.repo, self.identifier, runner=Runner())
        reference = engine.instance['role_profile_refs']['research_work'][-1]
        large = execution_profiles.resolve_profile(engine.instance['execution_profiles'], reference)
        large['input']['max_input_bytes'] = 2000000
        large['observation']['settings'].update(tool_review_window_seconds=60, self_check_response_window_seconds=5)
        large = execution_profiles.seal_profile(large)
        reference = execution_profiles.profile_ref(large)
        engine.instance['execution_profiles'][large['id']] = large
        small = deepcopy(large)
        small['input']['max_input_bytes'] = 500000
        small = execution_profiles.seal_profile(small)
        engine.instance['execution_profiles'][small['id']] = small
        from research_fixtures import FixtureAdapter
        for profile in (small, large):
            evidence = execution_profiles.capability_evidence(profile, FixtureAdapter().describe(),
                observed_at=engine.runtime['last_observed_utc'])
            engine.instance.setdefault('capability_evidence', {})[evidence['id']] = evidence
        task = task_fixture()
        task.update(title='Fixed input recovery', status='active', work_class='nonformal', inputs=[], reuse=[], dependencies=[], basis_refs=[],
            authority_refs=['GR-research'], profile_refs=[execution_profiles.profile_ref(small), reference],
            model_assessment={'difficulty': 'high', 'importance': 'high', 'reason': 'Preserve the assigned requirement'},
            question='Inspect the following fixed evidence: ' + 'required evidence ' * 40000, results=[])
        from research_fixtures import supply_observation_rules
        extensions = {}
        supply_observation_rules([task], extensions)
        task['initial_observation_rules'] = extensions['task_conditions'][0]['observation_rules']
        engine.runtime['tasks'] = {task['id']: task}
        approve_task(task, engine.instance, engine.runtime)
        action = {'id': 'AC-overflow-work', 'role': 'research_work', 'target': task['id'],
            'profile_ref': execution_profiles.profile_ref(small), 'grant_id': 'GR-research',
            'selected_contract_sha256': planning.contract_hash(task), 'model_assessment': deepcopy(task['model_assessment'])}
        engine.runtime['queue'] = [action]
        engine._save()
        engine.run(max_steps=1)
        self.assertEqual(calls, [])
        held = engine.runtime['waiting_actions'][action['id']]
        self.assertEqual(held['next_owner'], 'research_plan', held)
        owner, question = held['action']['owner_activity_id'], held['question_id']
        engine.run(max_steps=1)
        self.assertEqual([row['role'] for row in calls], ['research_plan'])
        retry = next(row for row in engine.runtime['queue'] if row['id'] == action['id'])
        self.assertEqual(retry['profile_ref'], reference)
        self.assertEqual(retry['owner_activity_id'], owner)
        self.assertEqual(next(q for q in engine.runtime['question_links'] if q['id'] == question)['status'], 'open')
        engine.run(max_steps=1)
        self.assertEqual([row['role'] for row in calls], ['research_plan', 'research_work'])
        self.assertEqual(calls[-1]['profile_ref'], reference)
        self.assertEqual(calls[-1]['owner_activity_id'], owner)
        self.assertEqual(next(q for q in engine.runtime['question_links'] if q['id'] == question)['status'], 'resolved')
        attempts = [e for e in engine.runtime['executions'].values() if e.get('action', {}).get('id') == action['id']]
        self.assertEqual(len(attempts), 2)
        self.assertEqual(len({e['id'] for e in attempts}), 2)
        self.assertTrue(any(e.get('outcome') == 'output_accepted' for e in attempts))


if __name__ == "__main__":
    import unittest
    unittest.main()
