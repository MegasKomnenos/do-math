"""Public input-overflow recovery against one actual temporary Git instance."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from do_math import execution_profiles
from do_math.engine import ResearchEngine
from do_math.repository import canonical_json
from test_engine import ScriptedRunner, formal_ok
from research_fixtures import FixtureAdapter, bare_engine, restore_template, run_cli
from state_fixtures import active_instance


# The active state every test here starts from (state_fixtures.active_instance).
ACTIVE_CONFIG = {'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5}


def active_repository():
    """A copy of the validated active state: ``(root, repository, instance ID)``."""
    root, identifier = restore_template(active_instance, config=ACTIVE_CONFIG)
    return root, root / "repository", identifier


def cli(root: Path, *arguments: str) -> dict:
    """The public command's result; the command must succeed."""
    completed = run_cli(*arguments, cwd=root)
    if completed.returncode != 0:
        raise AssertionError(completed.stdout + completed.stderr)
    envelope = json.loads(completed.stdout)
    if envelope["exit_code"] != 0:
        raise AssertionError(envelope)
    return envelope["result"]


def apply_limit(root: Path, repository: Path, identifier: str, limit: int, request_id: str) -> ResearchEngine:
    """Configure ``max_input_bytes`` publicly and record the new profiles' capability evidence."""
    config = root / (request_id + ".json")
    config.write_bytes(canonical_json({"max_input_bytes": limit}))
    accepted = cli(root, "configure", "--repository", str(repository), "--instance", identifier,
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
    with patch("do_math.initialization.adapter_for", return_value=FixtureAdapter()):
        apply_limit(root, repository, identifier, 1, "UC-limit-small")
        requested = cli(root, "request", "--repository", str(repository), "--instance", identifier,
                        "--role", "maintenance", "--reason", "Check the installed recovery boundary",
                        "--request-id", "UC-maintenance")
        if not requested["accepted"]:
            raise AssertionError(requested)
        ResearchEngine(repository, identifier, runner=ScriptedRunner(), formal_verifier=formal_ok).run(max_steps=1)
    return identifier


class InputRecoveryPublicTests(unittest.TestCase):
    def setUp(self) -> None:
        """A copy of the validated active state; other modules borrow this setUp.

        Sets ``root``, ``repo`` and ``identifier``.
        """
        adapter = patch("do_math.initialization.adapter_for", return_value=FixtureAdapter())
        adapter.start()
        self.addCleanup(adapter.stop)
        self.root, self.repo, self.identifier = active_repository()

    def overflowed(self) -> None:
        """Replace the copy with ``overflowed_maintenance``'s state."""
        self.root, self.identifier = restore_template(overflowed_maintenance)
        self.repo = self.root / "repository"

    def cli(self, *arguments: str) -> dict:
        return cli(self.root, *arguments)

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

        report_path = os.environ.get("INPUT_RECOVERY_REPORT")
        if report_path:
            report = {
                "repository_kind": "actual temporary Git",
                "external_doubles": ["model replies", "Lean verifier", "CLI capability response"],
                "instance_id": identifier,
                "action_id": action_id,
                "overflow_count": len(engine.runtime["input_overflows"]),
                "question_ids": [first_question_id, second_question_id],
                "public_question_text": public_question["text"],
                "same_request_replayed": replay["replayed"],
                "retry_event_counts": {kind: sum(row.get("kind") == kind for row in engine.runtime["history"])
                    for kind in ("input_overflow_retry_started", "input_overflow_retry_failed",
                                 "input_overflow_retry_resolved")},
                "resolved_profile_ref": resolved["profile_ref"],
                "resolved_prompt_bytes": resolved["prompt_bytes"],
                "resolved_limit_bytes": resolved["limit_bytes"],
                "closed_retry": {"exit_code": closed.returncode, "message": rejected["message"]},
                "final_status": engine.runtime["status"],
                "final_snapshot": engine.head,
            }
            destination = Path(report_path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(canonical_json(report))

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


if __name__ == "__main__":
    import unittest
    unittest.main()
