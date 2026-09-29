"""The engine's formal checks with a compiler double: continuation after controls, the required environment and the verifier's binding."""
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import create_autospec, Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import execution_profiles
from do_math.configuration import DEFAULT_CONFIG
from do_math.engine import ResearchEngine
from do_math.repository import ResearchRepository
from engine_fixtures import formal_check_engine, formal_verification, routing_engine
from research_fixtures import await_stop
from state_fixtures import owner_calls, start_active_copy


class FormalContinuationTests(unittest.TestCase):
    def make(self):
        return formal_check_engine(self)

    def stopped_check(self, arguments):
        """The check reads its stop flag until the owner's judgment sets it."""
        if not await_stop(arguments['should_stop'], timeout=5):
            raise AssertionError('the owner control did not reach the check')
        return {'status': 'stopped'}

    def run_with_control(self, engine, action, operation):
        """Start the check, apply the control on the owner, then judge stops as a publication does."""
        engine.formal_behavior = self.stopped_check
        with owner_calls(engine) as calls:
            engine._formal(action)
            engine.control(operation, {})
            calls.judge()

    def test_pause_resume_retains_one_action_and_reaches_identity_review(self):
        engine, action = self.make()
        self.run_with_control(engine, action, 'pause')
        first = next(e for e in engine.runtime['executions'].values() if e['role'] == 'formal_check')
        self.assertEqual(first['status'], 'ended')
        pending = next(a for a in engine.runtime['queue'] if a['id'] == action['id'])
        self.assertEqual(pending['continuation_of'], first['id'])
        self.assertNotEqual(engine.runtime['activities'][first['owner_activity_id']]['status'], 'finished')
        engine.control('resume', {})
        engine.control('resume', {})
        self.assertEqual(sum(a.get('id') == action['id'] for a in engine.runtime['queue']), 1)
        engine.formal_behavior = None
        with owner_calls(engine):
            engine._formal(pending)
        attempts = [e for e in engine.runtime['executions'].values() if e['role'] == 'formal_check']
        self.assertEqual(len(attempts), 2)
        self.assertEqual(attempts[-1]['continuation_of'], first['id'])
        self.assertEqual(attempts[-1]['formal_status'], 'verified')
        self.assertTrue(any(a['role'] == 'identity_review' for a in engine.runtime['queue']))

    def test_check_stopped_before_start_ends_and_returns_its_capacity(self):
        engine, action = self.make()
        engine.control('pause', {})
        with owner_calls(engine):
            engine._formal(action)
        execution = next(e for e in engine.runtime['executions'].values() if e['role'] == 'formal_check')
        self.assertEqual(engine.formal_calls, [])
        # Nothing started, so the launch returned and the capacity is free; the check is not held for recovery.
        self.assertEqual((execution['status'], execution['capacity']['local_termination']), ('ended', 'confirmed'))
        pending = next(a for a in engine.runtime['queue'] if a['id'] == action['id'])
        self.assertEqual(pending['continuation_of'], execution['id'])

    def test_close_preserves_the_ended_check_without_continuation(self):
        engine, action = self.make()
        self.run_with_control(engine, action, 'close')
        self.assertFalse(any(a.get('id') == action['id'] for a in engine.runtime['queue']))
        self.assertFalse(engine.runtime['waiting_actions'])

    def test_resume_rechecks_source_trust_and_authority_before_another_call(self):
        for changed in ('source', 'trust', 'authority'):
            with self.subTest(changed=changed):
                engine, action = self.make()
                self.run_with_control(engine, action, 'pause')
                engine.control('resume', {})
                continuation = next(a for a in engine.runtime['queue'] if a.get('id') == action['id'])
                if changed == 'source':
                    fid = engine.instance['knowledge']['K1']['formal_result_id']
                    engine.instance['formal_results'][fid]['lean_code'] += '\n-- changed candidate'
                elif changed == 'trust':
                    engine.instance['trust_environments'][engine.instance['active_trust_environment']]['status'] = 'inactive'
                else:
                    engine.instance['grants']['GR-research']['status'] = 'revoked'
                engine.formal_behavior = None
                with owner_calls(engine):
                    engine._formal(continuation)
                self.assertEqual(len(engine.formal_calls), 1)


class FormalAttemptLineageTests(unittest.TestCase):
    def setUp(self):
        start_active_copy(self)

    def test_public_pause_restart_resume_preserves_formal_attempt_lineage(self):
        from do_math import knowledge_records
        from research_fixtures import send_control
        engine = ResearchEngine(self.repo, self.identifier)
        environment = engine._formal_environment()
        engine.instance['config']['lean_command'] = environment['toolchain']['configured_command']
        editions = execution_profiles.build_profiles(engine.instance['config'])
        engine.instance['execution_profiles'].update(editions['execution_profiles'])
        engine.instance['role_profile_refs']['formal_check'] = editions['role_profile_refs']['formal_check']
        engine.instance, _ = knowledge_records.create_candidate(engine.instance, {
            'id': 'KN-formal-resume', 'kind': 'lemma', 'title': 'Resume fixture',
            'statement': 'One equals one', 'summary': 'Reflexivity',
            'lean_code': 'theorem resume_fixture : 1 = 1 := rfl', 'declaration_names': ['resume_fixture'],
            'dependencies': []}, source_ref=engine.instance['lifecycle']['input_id'],
            actor_ref=next(iter(engine.runtime['executions'])))
        engine._enqueue('formal_check', 'KN-formal-resume')
        engine._save()
        def pause(**arguments):
            # The owner publishes the pause; that publication sets this check's stop flag.
            if not await_stop(arguments['should_stop'], timeout=5):
                raise AssertionError('the published pause did not reach the check')
            return {'status': 'stopped', 'reason': 'Explicit test pause; no Lean process'}
        engine.formal_verifier = pause
        with owner_calls(engine):
            engine._formal(next(a for a in engine.runtime['queue'] if a['role'] == 'formal_check'))
            send_control(engine, 'pause', config={})
        first = next(e for e in engine.runtime['executions'].values() if e['role'] == 'formal_check')
        self.assertEqual(first['status'], 'ended')
        restarted = ResearchEngine(self.repo, self.identifier)
        send_control(restarted, 'resume', config={})
        action = next(a for a in restarted.runtime['queue'] if a['role'] == 'formal_check')
        self.assertEqual(action['continuation_of'], first['id'])
        restarted.formal_verifier = lambda **kw: formal_verification(
            kw['source'], kw['declarations'], kw['expected_toolchain'])
        with owner_calls(restarted):
            restarted._formal(action)
        final = ResearchEngine(self.repo, self.identifier)
        attempts = [e for e in final.runtime['executions'].values() if e['role'] == 'formal_check']
        self.assertEqual(len(attempts), 2)
        self.assertTrue(any(e.get('continuation_of') == first['id'] and e['formal_status'] == 'verified' for e in attempts))
        self.assertTrue(any(a['role'] == 'identity_review' for a in final.runtime['queue']))


def parked_formal_check():
    """An engine whose formal check ``AC-formal`` waits because no preapproved environment is active."""
    from do_math import knowledge_io
    engine = routing_engine()
    engine.instance.update(active_trust_environment=None, trust_environments={}, sources=[])
    engine.instance["config"] = deepcopy(DEFAULT_CONFIG)
    engine.instance.update(execution_profiles.build_profiles(engine.instance["config"]))
    engine.instance, engine.runtime, kid = knowledge_io.import_candidate(engine.instance, engine.runtime,
        {"kind": "theorem", "title": "T", "statement": "True", "summary": "True", "explanation": "A proof",
         "lean_code": "theorem t : True := by trivial", "declaration_names": ["t"], "dependencies": []},
        source_ref="EX-author", actor_ref="EX-author")
    # This isolates the actual trust-environment gate; public lifecycle/grant
    # admission is exercised by PublicGitFlow and LIFECYCLE's owner tests.
    engine._action_lifecycle_gate = create_autospec(engine._action_lifecycle_gate)
    engine._require_action_clock = create_autospec(engine._require_action_clock)
    engine.runtime["trust_transitions"] = {}
    engine.formal_verifier = Mock()
    engine._save = create_autospec(engine._save)
    engine._formal({"id": "AC-formal", "role": "formal_check", "target": kid})
    return engine


class FormalAuthority(unittest.TestCase):
    def test_missing_preapproved_environment_never_runs_or_autoapproves(self):
        engine = parked_formal_check()
        engine.formal_verifier.assert_not_called()
        self.assertIsNone(engine.instance["active_trust_environment"])
        self.assertEqual(next(iter(engine.runtime["activities"].values()))["status"], "waiting")

    def test_parked_check_returns_to_the_queue_once_an_environment_and_authority_admit_it(self):
        engine = parked_formal_check()
        engine._resume_formal_waits()
        self.assertIn("AC-formal", engine.runtime["waiting_actions"])
        engine._formal_environment = create_autospec(engine._formal_environment, return_value={"id": "TE-new"})
        with patch("do_math.governance.authorize", return_value={"allowed": True, "grant_id": "GR-one"}):
            engine._resume_formal_waits()
        self.assertNotIn("AC-formal", engine.runtime["waiting_actions"])
        self.assertIn("AC-formal", [action["id"] for action in engine.runtime["queue"]])

    def test_only_a_check_stopped_by_changed_conditions_resumes(self):
        engine = parked_formal_check()
        action = engine.runtime["waiting_actions"].pop("AC-formal")["action"]
        for identifier, reasons in (("AC-changed", ["authority_changed", "input_changed"]),
                                    ("AC-stopped", ["execution_stop_requested"])):
            engine.runtime["waiting_actions"][identifier] = {
                "action": {**action, "id": identifier}, "kind": "formal_stopped", "reason": ", ".join(reasons),
                "execution_id": "EX-" + identifier, "next_owner": "trust_governance",
                "detail": {"stop_reasons": reasons}}
        engine._formal_environment = create_autospec(engine._formal_environment, return_value={"id": "TE-new"})
        with patch("do_math.governance.authorize", return_value={"allowed": True, "grant_id": "GR-one"}):
            engine._resume_formal_waits()
        self.assertEqual(list(engine.runtime["waiting_actions"]), ["AC-stopped"])
        resumed = next(row for row in engine.runtime["queue"] if row["id"] == "AC-changed")
        self.assertEqual(resumed["continuation_of"], "EX-AC-changed")


class FormalBindingConnections(unittest.TestCase):
    def run_verifier(self, result):
        from do_math import knowledge_io
        engine = routing_engine()
        directory = tempfile.TemporaryDirectory(); self.addCleanup(directory.cleanup)
        config = {**deepcopy(DEFAULT_CONFIG), "lean_command": [sys.executable], }
        from research_fixtures import trust_environment, trust_fixture
        environment, binding = trust_environment(trust_fixture(Path(directory.name), [sys.executable]),
                                                 environment_id="TE-one", source_ref="fixture")
        engine.instance.update(workspace=directory.name, sources=[], config=config,
            active_trust_environment="TE-one", trust_environments={"TE-one": environment})
        engine.runtime["trust_bindings"] = {"TE-one": binding}
        engine.instance.update(execution_profiles.build_profiles(config))
        engine.instance["config"] = {**config, "lean_command": ["unapproved-config-command"], }
        engine.instance, engine.runtime, kid = knowledge_io.import_candidate(engine.instance, engine.runtime,
            {"kind": "theorem", "title": "T", "statement": "True", "summary": "True", "explanation": "A proof",
                "lean_code": "-- e\u0301\r\ntheorem t : True := by trivial", "declaration_names": ["t"], "dependencies": []}, source_ref="EX-author", actor_ref="EX-author")
        engine.head = "fixed-input"; engine._save = create_autospec(engine._save); engine._controls = create_autospec(engine._controls)
        engine._check_conversations = create_autospec(engine._check_conversations, return_value=False)
        engine._action_lifecycle_gate = create_autospec(engine._action_lifecycle_gate); engine._formal_environment = create_autospec(engine._formal_environment, return_value=deepcopy(environment))
        engine.formal_verifier = Mock(return_value=result)
        with patch("do_math.governance.authorize", return_value={"allowed": True, "grant_id": "GR-one"}),                 owner_calls(engine):
            engine._formal({"id": "AC-formal", "role": "formal_check", "target": kid})
        return engine, environment

    def test_verifier_uses_the_fixed_environment_command_and_fingerprint(self):
        engine, environment = self.run_verifier({"status": "failed", "reason": "compiler double, no proof claim"})
        kwargs = engine.formal_verifier.call_args.kwargs
        self.assertEqual(kwargs["lean_command"], [sys.executable])
        self.assertNotIn("timeout_seconds", kwargs)
        self.assertEqual(kwargs["expected_toolchain"], environment["toolchain"])
        self.assertEqual(set(kwargs["allowed_axioms"]), set(environment["allowed_axioms"]))
        self.assertEqual(next(e for e in engine.runtime["executions"].values() if e.get("role") == "formal_check")["outcome"], "execution_incomplete")

    def test_exact_compiler_keys_and_source_survive_result_artifacts(self):
        result = {"status": "failed", "reason": "compiler double retains exact names", "axioms": {"K": [], "K": []}}
        engine, _ = self.run_verifier(result)
        artifacts = {path: raw for call in engine._save.call_args_list if call.args for path, raw in call.args[0].items()}
        raw = next(raw for path, raw in artifacts.items() if path.endswith("formal.json"))
        self.assertEqual(json.loads(raw), result)
        source = next(raw for path, raw in artifacts.items() if path.endswith("proposal.lean"))
        self.assertEqual(source, engine.formal_verifier.call_args.kwargs["source"].encode("utf-8"))
        self.assertIn("e\u0301\r\n".encode("utf-8"), source)

    def test_publication_signature_distinguishes_exact_unicode_payload(self):
        # _save publishes unless _unchanged() finds the state equal to this head's published state.
        engine = routing_engine(); engine.head = "snapshot"
        engine.instance["formal_results"] = {"FR-one": {"lean_code": '-- "e\u0301"'}}
        engine.store = create_autospec(ResearchRepository, instance=True)
        engine.store.published_state.return_value = (deepcopy(engine.instance), deepcopy(engine.runtime))
        self.assertTrue(engine._unchanged())
        engine.store.published_state.assert_called_with("snapshot")
        engine.instance["formal_results"]["FR-one"]["lean_code"] = '-- "é"'
        self.assertFalse(engine._unchanged())


if __name__ == "__main__":
    unittest.main()
