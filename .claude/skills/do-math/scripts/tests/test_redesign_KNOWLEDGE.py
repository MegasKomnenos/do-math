"""Knowledge family, ontology, impact, and installed Lean regression contracts."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_categories import test_group as category
from do_math import knowledge, knowledge_io
from do_math import knowledge_records as kr
import hashlib
import tempfile
import subprocess
from unittest.mock import patch
from do_math.formal import verify_lean, discover_lean, portable_bin, toolchain_root
import inspect
import os


def candidate(**changes):
    return dict(kind="theorem", title="Truth", statement="True", explanation="Truth holds",
                summary="Truth", lean_code="theorem truth : True := True.intro",
                declaration_names=["truth"], dependencies=[], **changes)


class KnowledgeRedesign(unittest.TestCase):
    @category('lean')
    def test_installed_lean_extracts_transitive_constants(self):
        command = [os.environ.get("DO_MATH_KNOWLEDGE_TEST_LEAN", str(portable_bin(toolchain_root()) / "lean.exe"))]
        if not Path(command[0]).is_file():
            self.skipTest("installed Lean is unavailable")
        # Use the installed compiler through its actual local Job transport.
        with tempfile.TemporaryDirectory() as directory:
            result = verify_lean(source="def base : Nat := 1\ndef mid : Nat := base\ntheorem leaf : mid = base := rfl",
                declarations=["leaf"], workspace=Path(directory), lean_command=command)
        self.assertEqual(result["status"], "verified", result)
        self.assertIn("dependency_closure", result)
        self.assertIn("base", result["dependency_closure"]["leaf"])
        self.assertIn("mid", result["dependency_closure"]["leaf"])
        self.assertIn("leaf", result["declaration_evidence"])

    def verified(self, environment=None, *, identity=True):
        state, runtime, kid = knowledge_io.import_candidate({}, {}, candidate(), source_ref="source", actor_ref="producer")
        state.update(active_trust_environment="TE-test", trust_environments={"TE-test": {
            "id": "TE-test", "status": "active", "toolchain": {"version": "test-fixture"}, "allowed_axioms": []}})
        if environment is not None:
            state['trust_environments']['TE-test'] = copy.deepcopy(environment)
        verification = {"status": "verified", "source_sha256": hashlib.sha256(candidate()["lean_code"].encode()).hexdigest(),
            "declarations": ["truth"], "toolchain": {"version": "test-fixture"}, "axioms": {"truth": []},
            "dependency_closure": {"truth": ["True", "True.intro"]},
            "dependency_evidence": {"truth": {"True": "fixture-type", "True.intro": "fixture-constructor"}},
            "declaration_evidence": {"truth": {"type": "True", "value": "True.intro"}}}
        verification['toolchain'] = copy.deepcopy(state['trust_environments']['TE-test']['toolchain'])
        state = kr.record_formal_result(state, kid, verification, "TE-test", runtime=runtime)
        if not identity:
            return state, runtime, kid, None
        state, aid = kr.record_identity_assessment(state, kid,
            {"decision": "match", "basis": kr.identity_basis(state, kid), "review_cycle_id": "RC-fixture"}, "policy:1", runtime=runtime)
        return state, runtime, kid, aid

    def test_import_separates_formal_and_exposition_authority(self):
        state, runtime, kid = knowledge_io.import_candidate({}, {}, candidate(), source_ref="source", actor_ref="producer")
        record = state["knowledge"][kid]
        self.assertNotIn("lean_code", record)
        self.assertNotIn("formal", record)
        self.assertIn(record["formal_result_id"], state["formal_results"])
        self.assertIn(record["exposition_id"], state["expositions"])

    def test_relation_templates_are_not_active_instance_definitions(self):
        state = knowledge_io.ensure_ontology({})
        self.assertFalse(knowledge_io.catalog_definitions(state)["relations"])

    def test_kind_registration_requires_explicit_check_and_activation(self):
        definition = dict(family="knowledge", token="bounded_result", meaning="A bounded result", constraints={})
        state, token = knowledge_io.register_kind_definition({}, definition, source_ref="source", actor_ref="producer")
        definition = next(r for r in state["kind_definitions"].values() if r["token"] == token)
        self.assertEqual(definition["status"], "candidate")

    def test_kind_definitions_use_record_ids_and_allow_explicit_replacement(self):
        state = knowledge_io.ensure_ontology({})
        self.assertTrue(all(key == value["id"] for key, value in state["kind_definitions"].items()))
        state, runtime = knowledge_io.withdraw_kind_definition(state, {}, "knowledge", "theorem", reason="replacement", actor_ref="review")
        state, token = knowledge_io.register_kind_definition(state,
            {"family": "knowledge", "token": "theorem", "meaning": "Revised theorem kind", "constraints": {}},
            source_ref="revision", actor_ref="author")
        replacement = next(d for d in state["kind_definitions"].values() if d["token"] == token and d["status"] == "candidate")
        self.assertIn(replacement["supersedes"], state["kind_definitions"])

    def test_impact_planning_does_not_mutate_and_includes_relations(self):
        state = {"knowledge": {"KN-a": {"id": "KN-a", "lifecycle": "active"}},
                 "relations": [{"id": "RL-a", "source": "KN-a", "target": "KN-a", "status": "active"}]}
        before = copy.deepcopy(state)
        self.assertTrue(callable(getattr(knowledge, "plan_impact", None)), "missing non-mutating impact planner")
        plan = knowledge.plan_impact(state, {}, ["KN-a"], ["RL-a"])
        self.assertEqual(state, before)
        self.assertIn("RL-a", plan["computed_impact"])

    def test_explanation_revision_preserves_formal_evidence_and_old_judgment(self):
        state, runtime, kid, aid = self.verified()
        formal = copy.deepcopy(state["formal_results"])
        assessment = copy.deepcopy(state["identity_assessments"][aid])
        declared = [aid, next(u["id"] for u in state["assessment_uses"].values() if u["assessment_id"] == aid)]
        revised, _ = knowledge.revise_knowledge(state, runtime, kid, {"summary": "Revised summary"},
            reason="clarify", actor_ref="author", declared_impact=declared)
        self.assertEqual(revised["formal_results"], formal)
        self.assertEqual(revised["identity_assessments"][aid], assessment)
        self.assertEqual(revised["knowledge"][kid]["lifecycle"], "superseded")
        replacements = [r for r in revised["knowledge"].values() if r.get("supersedes") == kid]
        self.assertEqual(len(replacements), 1)
        self.assertFalse(knowledge.assess_use(replacements[0], revised)["valid"])
        old_use = next(u for u in revised["assessment_uses"].values() if u["assessment_id"] == aid)
        self.assertEqual(old_use["status"], "suspended")
        self.assertEqual(revised["expositions"][state["knowledge"][kid]["exposition_id"]]["lifecycle"], "superseded")

    def test_decision_reference_reports_actual_split_environment(self):
        state, runtime, kid, aid = self.verified()
        self.assertEqual(knowledge.decision_reference(state["knowledge"][kid], state)["trust_environment_id"], "TE-test")

    def test_revision_reuses_candidate_kind_and_dependency_validation(self):
        state, runtime, kid, aid = self.verified()
        declared = [aid, next(u["id"] for u in state["assessment_uses"].values() if u["assessment_id"] == aid)]
        for changes in ({"kind": "unregistered_kind"}, {"dependencies": ["KN-missing"]}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                knowledge.revise_knowledge(state, runtime, kid, changes, reason="revision", actor_ref="author", declared_impact=declared)

    def test_import_captures_required_source_and_rejects_unknown_source(self):
        state = {"sources": [{"name": "paper", "path": "research/sources/paper.txt", "sha256": "original"}]}
        with self.assertRaises(ValueError):
            knowledge_io.import_candidate(state, {}, candidate(source_refs=["absent"]), source_ref="submission", actor_ref="author")
        changed, _, kid = knowledge_io.import_candidate(state, {}, candidate(source_refs=["paper"]), source_ref="submission", actor_ref="author")
        self.assertEqual(changed["knowledge"][kid]["source_basis"][0]["sha256"], "original")

    def test_assessment_suspension_is_local_and_reversible(self):
        state, runtime, kid, aid = self.verified()
        before = copy.deepcopy(state["identity_assessments"])
        suspended = kr.set_assessment_use(state, aid, "suspended", "review defect", "reviewer")
        self.assertEqual(suspended["identity_assessments"], before)
        self.assertFalse(knowledge.assess_use(suspended["knowledge"][kid], suspended)["valid"])
        self.assertTrue(kr.knowledge_view(suspended)[0]["formal_valid"])
        restored = kr.set_assessment_use(suspended, aid, "active", "defect resolved", "reviewer")
        self.assertTrue(knowledge.assess_use(restored["knowledge"][kid], restored)["valid"])

    def test_independent_expositions_share_one_formal_result(self):
        state, runtime, kid, aid = self.verified()
        fid = state["knowledge"][kid]["formal_result_id"]
        data = candidate(formal_result_ref=fid)
        data["explanation"] = "A second explanation"
        state, runtime, other = knowledge_io.import_candidate(state, runtime, data, source_ref="second-source", actor_ref="other-author")
        self.assertEqual(len(state["formal_results"]), 1)
        self.assertEqual(runtime["queue"][-1]["role"], "identity_review")
        state, second_assessment = kr.record_identity_assessment(state, other,
            {"decision": "match", "basis": kr.identity_basis(state, other)}, "policy:1", runtime=runtime)
        state = kr.set_assessment_use(state, aid, "suspended", "first explanation defect", "reviewer")
        self.assertFalse(knowledge.assess_use(state["knowledge"][kid], state)["valid"])
        self.assertTrue(knowledge.assess_use(state["knowledge"][other], state)["valid"])

    def test_mathematical_relation_consumes_separate_result_and_assessment(self):
        state, runtime, kid, aid = self.verified()
        template = next(t for t in knowledge_io.relation_templates() if t["token"] == "formally_implies")
        state, token = knowledge_io.register_kind_definition(state, template, source_ref="template", actor_ref="author")
        state = knowledge_io.check_kind_definition(state, "relation", token, check_ref="check", actor_ref="checker")
        state = knowledge_io.activate_kind_definition(state, "relation", token, approval_ref="review", actor_ref="reviewer")
        fid = state["knowledge"][kid]["formal_result_id"]
        claim = {"kind": token, "source": kid, "target": kid, "confirmed_scope": "reflexive implication"}
        state["formal_results"][fid]["relation_claim"] = claim
        state["identity_assessments"][aid]["relation_claim"] = claim
        relation = {**claim, "formal_result_refs": [fid], "assessment_refs": [aid], "evidence_refs": [kid]}
        self.assertTrue(knowledge_io.validate_relation(state, relation)["valid"])
        stopped = kr.set_assessment_use(state, aid, "suspended", "recheck", "reviewer")
        self.assertFalse(knowledge_io.validate_relation(stopped, relation)["valid"])

    def test_relation_claim_is_bound_through_import_and_identity(self):
        state, runtime, kid, aid = self.verified()
        template = next(t for t in knowledge_io.relation_templates() if t["token"] == "formally_implies")
        state, token = knowledge_io.register_kind_definition(state, template, source_ref="template", actor_ref="author")
        state = knowledge_io.check_kind_definition(state, "relation", token, check_ref="check", actor_ref="checker")
        state = knowledge_io.activate_kind_definition(state, "relation", token, approval_ref="review", actor_ref="reviewer")
        claim = {"kind": token, "source": kid, "target": kid, "confirmed_scope": "reflexive"}
        state, runtime, proof = knowledge_io.import_candidate(state, runtime, candidate(relation_claim=claim), source_ref="source", actor_ref="author")
        verification = copy.deepcopy(state["formal_results"][state["knowledge"][kid]["formal_result_id"]]["verification"])
        state = kr.record_formal_result(state, proof, verification, "TE-test", runtime=runtime)
        state, identity = kr.record_identity_assessment(state, proof,
            {"decision": "match", "basis": kr.identity_basis(state, proof)}, "policy:1", runtime=runtime)
        relation = {**claim, "formal_result_refs": [state["knowledge"][proof]["formal_result_id"]],
                    "assessment_refs": [identity], "evidence_refs": [kid]}
        self.assertTrue(knowledge_io.validate_relation(state, relation)["valid"])
        state["knowledge"][kid]["title"] = "changed endpoint"
        self.assertFalse(knowledge_io.validate_relation(state, relation)["valid"])

    def test_trust_transition_uses_split_results_and_compares_evidence(self):
        state, runtime, kid, aid = self.verified()
        state["trust_environments"]["TE-next"] = {"id": "TE-next", "status": "registered", "toolchain": {"version": "next"}, "allowed_axioms": []}
        transition = knowledge.begin_transition(state, "TE-next")
        self.assertEqual(len(transition["targets"]), 1)
        self.assertIn("dependency_closure", transition["targets"][0])
        self.assertIn("axioms", transition["targets"][0])
        result = copy.deepcopy(state["formal_results"][state["knowledge"][kid]["formal_result_id"]]["verification"])
        result.update(id=kid, toolchain={"version": "next"})
        transition = knowledge.record_transition_result(state, transition, result)
        activated = knowledge.activate_transition(state, transition)
        self.assertEqual(activated["active_trust_environment"], "TE-next")
        self.assertTrue(knowledge.assess_use(activated["knowledge"][kid], activated)["valid"])
        self.assertEqual(activated["identity_assessments"][aid], state["identity_assessments"][aid])
        result["dependency_evidence"]["truth"]["True"] = "changed-type"
        transition = knowledge.record_transition_result(state, knowledge.begin_transition(state, "TE-next"), result)
        with self.assertRaises(ValueError):
            knowledge.activate_transition(state, transition)

    def test_environment_recovery_restores_only_environment_suspension(self):
        for semantic in (False, True):
            state, runtime, kid, aid = self.verified()
            if semantic:
                state = kr.set_assessment_use(state, aid, "suspended", "semantic defect", "reviewer")
            state, runtime = knowledge.invalidate_environment(state, runtime, "TE-test", "environment defect")
            state["trust_environments"]["TE-next"] = {"id": "TE-next", "status": "registered", "toolchain": {"version": "next"}, "allowed_axioms": []}
            transition = knowledge.begin_transition(state, "TE-next")
            result = copy.deepcopy(state["formal_results"][state["knowledge"][kid]["formal_result_id"]]["verification"])
            result.update(id=kid, toolchain={"version": "next"})
            transition = knowledge.record_transition_result(state, transition, result)
            activated = knowledge.activate_transition(state, transition)
            self.assertEqual(knowledge.assess_use(activated["knowledge"][kid], activated)["valid"], not semantic)

    def test_identity_review_cannot_replace_missing_new_kernel_evidence(self):
        state, runtime, kid, aid = self.verified()
        state["trust_environments"]["TE-next"] = {"id": "TE-next", "status": "registered", "toolchain": {"version": "next"}, "allowed_axioms": []}
        transition = knowledge.begin_transition(state, "TE-next")
        result = copy.deepcopy(state["formal_results"][state["knowledge"][kid]["formal_result_id"]]["verification"])
        result.update(id=kid, toolchain={"version": "next"})
        result.pop("dependency_closure")
        result["identity_review"] = {"decision": "match", "result_digest": kr.digest(result), "review_ref": "review", "policy_ref": "policy:1"}
        transition = knowledge.record_transition_result(state, transition, result)
        with self.assertRaises(ValueError):
            knowledge.activate_transition(state, transition)

    def test_rejects_unapproved_environment_and_replayed_identity_basis(self):
        state, runtime, kid, aid = self.verified()
        assessment = {"decision": "match", "basis": {"formal": "old", "exposition": "old"}}
        with self.assertRaises(ValueError):
            kr.record_identity_assessment(state, kid, assessment, "policy:1", runtime=runtime)
        result = state["formal_results"][state["knowledge"][kid]["formal_result_id"]]["verification"]
        state["trust_environments"]["TE-test"]["status"] = "registered"
        with self.assertRaises(ValueError):
            kr.record_formal_result(state, kid, result, "TE-test", runtime=runtime)

    def test_storage_registration_roundtrip_uses_split_family_files(self):
        from do_math.repository import ResearchRepository, new_id
        from do_math.state_contract import default_state_contract
        self.assertTrue(callable(getattr(kr, "register_storage_families", None)), "missing storage registration")
        contract = default_state_contract()
        kr.register_storage_families(contract)
        with tempfile.TemporaryDirectory() as directory:
            # Real Git and domain validators; compiler/reviewer/approval evidence is synthetic.
            from research_fixtures import trust_fixture
            from do_math.initialization import digest, trust_environment_errors
            from do_math.execution_profiles import build_profiles, profile_ref
            from do_math.engine import DEFAULT_CONFIG
            from do_math import activities, execution_lifecycle
            from do_math.review_cycle import accept_result, next_actions
            from do_math.review_engine import ReviewEngineMixin
            from test_review_cycle import scoped_start
            environment = trust_fixture(Path(directory), ['synthetic-lean'])
            environment.pop('operation')
            environment.update(id='TE-test', status='active', source_ref='synthetic:approval',
                               manifest_sha256=digest(environment['manifest']))
            self.assertEqual(trust_environment_errors(environment), [])
            state, runtime, kid, _ = self.verified(environment, identity=False)
            state['feature_version'] = runtime['feature_version'] = 5
            profiles = build_profiles(DEFAULT_CONFIG)
            profile = next(p for p in profiles['execution_profiles'].values() if p['role'] == 'identity_review')
            state.update(execution_profiles={profile['id']: profile}, capacity_constraints=profiles['capacity_constraints'])
            activity = activities.open_activity(runtime, activity_id=new_id('AT'), activity_kind='identity_review',
                owner_ref=kid, input_refs=[kid], opened_at='2026-09-20T00:00:00Z')
            cycle = scoped_start({**kr.proposal_view(state, kid), 'revision': 1}, reviewers=2)
            for _ in range(2):
                action = next_actions(cycle)[0]
                eid = new_id('EX')
                output = dict(proposal_digest=cycle['proposal_digest'], summary='Synthetic complete review',
                    used_sources=['proposal'], questions=[], decision='match', scope_complete=True, findings=[])
                cycle = accept_result(cycle, action, output, eid)
                execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=activity['id'],
                    actor_kind='ai', input_manifest={'proposal_digest': cycle['proposal_digest']},
                    profile_ref=profile_ref(profile), created_at='2026-09-20T00:00:00Z')
                execution.update(role='identity_review')
                activities.assign_execution(runtime, activity['id'], execution)
                for status in ('starting', 'running'):
                    execution_lifecycle.transition_execution(execution, status, at='2026-09-20T00:00:00Z')
                execution['submission_receipt'] = {'state': 'accepted', 'evidence_ref': 'synthetic:review'}
                execution_lifecycle.transition_execution(execution, 'stopping', at='2026-09-20T00:00:00Z', stop_phase='terminating')
                execution_lifecycle.transition_execution(execution, 'ended', at='2026-09-20T00:00:00Z', outcome='output_accepted')
            self.assertEqual(cycle['status'], 'completed')
            cycle.update(id=new_id('RC'), knowledge_id=kid, identity_basis=kr.identity_basis(state, kid), policy_ref='policy:fixture')
            runtime['review_cycles'] = {cycle['id']: cycle}
            assessment = ReviewEngineMixin._identity_assessment(cycle, reason='Synthetic sealed review')
            state, aid = kr.record_identity_assessment(state, kid,
                {**assessment, 'basis': cycle['identity_basis']}, cycle['policy_ref'], runtime=runtime)
            subprocess.run(["git", "init", "-q", directory], check=True)
            repo = ResearchRepository(Path(directory), new_id("RI"), contract=contract)
            repo.initialize(state, runtime)
            head, loaded, loaded_runtime = repo.load()
            self.assertEqual(loaded["formal_results"], state["formal_results"])
            self.assertEqual(loaded["identity_assessments"], state["identity_assessments"])
            self.assertTrue(knowledge.assess_use(loaded["knowledge"][kid], loaded)["valid"])

    def test_import_rejects_malformed_registry_id(self):
        with self.assertRaises(ValueError):
            knowledge_io.import_candidate({}, {}, candidate(id="KN-not-a-ulid"), source_ref="source", actor_ref="author")

    def test_formal_verification_requires_dependency_body_evidence(self):
        state, runtime, kid = knowledge_io.import_candidate({}, {}, candidate(), source_ref="source", actor_ref="producer")
        fixture, _, _, _ = self.verified()
        state.update(active_trust_environment="TE-test", trust_environments=fixture["trust_environments"])
        verification = copy.deepcopy(next(iter(fixture["formal_results"].values()))["verification"])
        verification.pop("dependency_evidence")
        with self.assertRaises(ValueError):
            kr.record_formal_result(state, kid, verification, "TE-test", runtime=runtime)

    def test_changed_approved_toolchain_rejects_before_source_execution(self):
        self.assertIn("expected_toolchain", inspect.signature(verify_lean).parameters)
        from do_math import formal
        binary_hash = hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()
        approved = dict(executable=sys.executable, sha256=binary_hash, configured_command=[sys.executable],
            version='approved-version', version_exit=0, project=None,
            verifier_sha256=hashlib.sha256(Path(formal.__file__).read_bytes()).hexdigest(),
            executables={str(Path(sys.executable).resolve()): binary_hash})
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "lean.exe"
            executable.write_bytes(b"approved executable bytes")
            command = [str(executable)]
            digest = hashlib.sha256(executable.read_bytes()).hexdigest()
            approved.update(executable=str(executable), sha256=digest, configured_command=command,
                            executables={str(executable.resolve()): digest})
            executable.write_bytes(b"changed executable bytes")
            with patch("do_math.formal._job_run", side_effect=AssertionError("changed executable must not start")) as run:
                result = verify_lean(source=candidate()["lean_code"], declarations=["truth"], workspace=Path(directory),
                    lean_command=command, expected_toolchain=approved)
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason"], "approved toolchain changed before execution")
        run.assert_not_called()

    def test_publication_reads_runtime_transition_barrier(self):
        self.assertIn("runtime", inspect.signature(kr.record_formal_result).parameters)
        state, runtime, kid, aid = self.verified()
        runtime["trust_transitions"] = {"TR-test": {"status": "checking"}}
        result = state["formal_results"][state["knowledge"][kid]["formal_result_id"]]["verification"]
        with self.assertRaises(ValueError):
            kr.record_formal_result(state, kid, result, "TE-test", runtime=runtime)
        with self.assertRaises(ValueError):
            kr.record_identity_assessment(state, kid, {"decision": "match", "basis": kr.identity_basis(state, kid)}, "policy:1", runtime=runtime)

    def test_impact_mismatch_and_staleness_reject_without_mutation(self):
        state = {"knowledge": {"KN-a": {"id": "KN-a", "lifecycle": "active"}},
                 "relations": [{"id": "RL-a", "source": "KN-a", "target": "KN-a", "status": "active"}]}
        before = copy.deepcopy(state)
        mismatch = knowledge.plan_impact(state, {}, ["KN-a"], [])
        with self.assertRaises(ValueError):
            knowledge.apply_impact(state, {}, mismatch, reason="change")
        self.assertEqual(state, before)
        plan = knowledge.plan_impact(state, {}, ["KN-a"], ["RL-a"])
        state["relations"][0]["target"] = "KN-changed"
        with self.assertRaises(ValueError):
            knowledge.apply_impact(state, {}, plan, reason="change")

    def test_impact_tracks_origin_refs_and_missing_split_refs(self):
        state = {"knowledge": {"KN-a": {"id": "KN-a", "lifecycle": "active"},
                               "KN-b": {"id": "KN-b", "lifecycle": "active", "origin_refs": ["KN-a"], "formal_result_refs": ["FR-missing"]}}}
        plan = knowledge.plan_impact(state, {}, ["KN-a"], ["KN-b"])
        self.assertIn("KN-b", plan["computed_impact"])
        self.assertIn("FR-missing", plan["unresolved_refs"])

    def test_impact_preserves_terminal_task_and_suspends_its_judgment(self):
        state = {"knowledge": {"KN-a": {"id": "KN-a", "lifecycle": "active"}},
                 "goal_judgments": [{"id": "GJ-a", "used_sources": ["KN-a"], "current": True}]}
        runtime = {"tasks": {"TK-a": {"id": "TK-a", "status": "completed", "inputs": ["KN-a"], "assessment": {"current": True}}}}
        plan = knowledge.plan_impact(state, runtime, ["KN-a"], ["TK-a", "GJ-a"])
        changed, run = knowledge.apply_impact(state, runtime, plan, reason="premise changed")
        self.assertEqual(run["tasks"]["TK-a"]["status"], "completed")
        self.assertFalse(run["tasks"]["TK-a"]["assessment"]["current"])
        self.assertFalse(changed["goal_judgments"][0]["current"])

    def test_kind_constraints_and_withdrawal(self):
        definition = dict(family="knowledge", token="bounded_result", meaning="A bounded result",
                          constraints={"allowed_epistemic_statuses": ["tentative"], "required_fields": ["confirmed_scope"]})
        state, token = knowledge_io.register_kind_definition({}, definition, source_ref="source", actor_ref="author")
        with self.assertRaises(ValueError):
            knowledge_io.activate_kind_definition(state, "knowledge", token, approval_ref="review", actor_ref="reviewer")
        state = knowledge_io.check_kind_definition(state, "knowledge", token, check_ref="check", actor_ref="checker")
        state = knowledge_io.activate_kind_definition(state, "knowledge", token, approval_ref="review", actor_ref="reviewer")
        data = candidate(); data["kind"] = token
        with self.assertRaises(ValueError):
            knowledge_io.import_candidate(state, {}, data, source_ref="source", actor_ref="author")
        data.update(epistemic_status="tentative", confirmed_scope="finite case")
        state, runtime, kid = knowledge_io.import_candidate(state, {}, data, source_ref="source", actor_ref="author")
        state, runtime = knowledge_io.withdraw_kind_definition(state, runtime, "knowledge", token, reason="bad semantics", actor_ref="reviewer")
        self.assertTrue(state["knowledge"][kid]["kind_use_suspended"])

    def test_environment_scoped_invalidation(self):
        state, runtime, kid, aid = self.verified()
        fid = state["knowledge"][kid]["formal_result_id"]
        unaffected, _ = knowledge.invalidate_environment(state, runtime, "TE-test", "constant defect",
            affected_constants=["NotUsed"], scope_evidence="checked constant boundary")
        self.assertEqual(unaffected["formal_results"][fid]["formal_use"], "active")
        affected, _ = knowledge.invalidate_environment(state, runtime, "TE-test", "constant defect",
            affected_constants=["True.intro"], scope_evidence="checked constant boundary")
        self.assertEqual(affected["formal_results"][fid]["formal_use"], "suspended")


class KnowledgeAudit2(unittest.TestCase):
    """Actual Git roundtrips with domain-produced sealed, synthetic reviews."""

    def setUp(self):
        from do_math.repository import ResearchRepository, new_id
        from do_math.engine import DEFAULT_CONFIG
        from do_math.execution_profiles import build_profiles
        from do_math.initialization import digest
        from research_fixtures import trust_fixture
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.repo = ResearchRepository(self.root, new_id('RI'))
        environment = trust_fixture(self.root, ['synthetic-lean'])
        environment.pop('operation')
        environment.update(id='TE-test', status='active', source_ref='synthetic:approval',
                           manifest_sha256=digest(environment['manifest']))
        self.state, self.runtime, self.kid, _ = KnowledgeRedesign().verified(environment, identity=False)
        self.state['feature_version'] = self.runtime['feature_version'] = 5
        profiles = build_profiles({**DEFAULT_CONFIG, 'lean_command': ['synthetic-lean']})
        self.profile = next(p for p in profiles['execution_profiles'].values() if p['role'] == 'identity_review')
        self.state.update(execution_profiles={self.profile['id']: self.profile}, capacity_constraints=profiles['capacity_constraints'])

    def cycle(self, decision='match', proposal=None):
        from do_math.repository import new_id
        from do_math import activities, execution_lifecycle
        from do_math.execution_profiles import profile_ref
        from do_math.review_cycle import accept_result, next_actions, start_review
        from test_review_cycle import scoped_start, ReviewCycleTests
        cid = new_id('RC')
        proposal = proposal or {**kr.proposal_view(self.state, self.kid), 'revision': 1}
        scoped = scoped_start(proposal, reviewers=2, max_rounds=1)
        cycle = start_review(proposal, reviewers=2, max_rounds=1, policy=scoped['review_policy'])
        activity = activities.open_activity(self.runtime, activity_id=new_id('AT'), activity_kind='identity_review',
            owner_ref=cid, input_refs=[self.kid], opened_at='2026-09-20T00:00:00Z')
        while next_actions(cycle):
            action = next_actions(cycle)[0]
            output = ReviewCycleTests().output(cycle, action['stage'])
            if action['stage'] == 'scope':
                output.update(scope_complete=True, scope_assessment=scoped['scope_assessment'])
            elif action['stage'] == 'initial' and decision == 'mismatch' and action['slot'] == 'initial-0':
                output.update(decision='mismatch', findings=[{'id': 'objection', 'statement': 'Scope mismatch', 'evidence': ['proposal']}])
            elif action['stage'] == 'initial' and decision == 'unresolved':
                output.update(decision='unresolved', scope_complete=False)
            eid = new_id('EX')
            cycle = accept_result(cycle, action, output, eid)
            execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=activity['id'],
                actor_kind='ai', input_manifest={'proposal_digest': cycle['proposal_digest']},
                profile_ref=profile_ref(self.profile), created_at='2026-09-20T00:00:00Z')
            action_id = new_id('AC')
            execution.update(role='identity_review', action={'id': action_id, 'lineage_id': action_id,
                'role': 'identity_review', 'target': self.kid, 'review_cycle_id': cid, **action}, output=output)
            activities.assign_execution(self.runtime, activity['id'], execution)
            for status in ('starting', 'running'):
                execution_lifecycle.transition_execution(execution, status, at='2026-09-20T00:00:00Z')
            execution['submission_receipt'] = {'state': 'accepted', 'evidence_ref': 'synthetic:review'}
            execution_lifecycle.transition_execution(execution, 'stopping', at='2026-09-20T00:00:00Z', stop_phase='terminating')
            execution_lifecycle.transition_execution(execution, 'ended', at='2026-09-20T00:00:00Z', outcome='output_accepted')
        self.assertEqual(cycle['decision'], decision)
        cycle.update(id=cid, knowledge_id=self.kid, identity_basis=kr.identity_basis(self.state, self.kid), policy_ref='policy:fixture')
        self.runtime.setdefault('review_cycles', {})[cid] = cycle
        return cycle

    def assessment(self, decision='match'):
        from do_math.review_engine import ReviewEngineMixin
        cycle = self.cycle(decision)
        assessment = ReviewEngineMixin._identity_assessment(cycle, reason='Synthetic sealed review')
        self.state, aid = kr.record_identity_assessment(self.state, self.kid,
            {**assessment, 'basis': cycle['identity_basis']}, cycle['policy_ref'], runtime=self.runtime)
        return aid

    def roundtrip(self):
        if not hasattr(self, 'head'):
            self.head = self.repo.initialize(self.state, self.runtime)
        else:
            self.head = self.repo.save_with_state(self.head, self.state, self.runtime)[0]
        self.head, self.state, self.runtime = self.repo.load()

    def test_shared_formal_result_continuity_round_trips_for_each_exposition(self):
        first = self.kid
        first_assessment = self.assessment()
        shared = self.state["knowledge"][first]["formal_result_id"]
        proposed = candidate(formal_result_ref=shared)
        proposed.update(title="Second explanation", explanation="An independent account of True")
        self.state, self.runtime, second = knowledge_io.import_candidate(
            self.state, self.runtime, proposed, source_ref="second-source", actor_ref="second-author")
        self.kid = second
        second_assessment = self.assessment()
        self.roundtrip()
        self.assertEqual(self.state["knowledge"][second]["formal_result_id"], shared)
        previous_assessments = {first: first_assessment, second: second_assessment}
        for environment_id in ("TE-next", "TE-third"):
            current_environment = self.state["active_trust_environment"]
            self.state["trust_environments"][environment_id] = {
                **copy.deepcopy(self.state["trust_environments"][current_environment]),
                "id": environment_id, "status": "registered"}
            transition = knowledge.begin_transition(self.state, environment_id)
            self.assertEqual({target["id"] for target in transition["targets"]}, {first, second})
            for target in transition["targets"]:
                self.assertEqual(target["exposition_id"],
                                 self.state["knowledge"][target["id"]]["exposition_id"])
                result = copy.deepcopy(self.state["formal_results"][target["formal_result_id"]]["verification"])
                result.update(id=target["id"], toolchain=copy.deepcopy(
                    self.state["trust_environments"][environment_id]["toolchain"]))
                transition = knowledge.record_transition_result(self.state, transition, result)
            self.runtime.setdefault("trust_transitions", {})[transition["id"]] = transition
            self.roundtrip()
            transition = self.runtime["trust_transitions"][transition["id"]]
            self.state = knowledge.activate_transition(self.state, transition)
            transition["status"] = "active"
            self.roundtrip()
            for kid, old_assessment in list(previous_assessments.items()):
                inherited = next(row for row in self.state["identity_assessments"].values()
                                 if row.get("previous_assessment_id") == old_assessment)
                self.assertEqual(self.state["expositions"][inherited["exposition_id"]]["supersedes"],
                                 self.state["identity_assessments"][old_assessment]["exposition_id"])
                self.assertTrue(kr.usable_links(self.state, kid))
                previous_assessments[kid] = inherited["id"]
            broken = copy.deepcopy(self.runtime)
            targets = broken["trust_transitions"][transition["id"]]["targets"]
            targets[0]["exposition_id"] = targets[1]["exposition_id"]
            with self.assertRaises(ValueError):
                self.repo.validate_candidate(self.state, broken)
            missing = copy.deepcopy(self.runtime)
            del missing["trust_transitions"][transition["id"]]["targets"][0]["exposition_id"]
            with self.assertRaises(ValueError):
                self.repo.validate_candidate(self.state, missing)

    def test_unicode_currentness_and_impact_survive_actual_storage(self):
        self.assessment()
        self.state['knowledge'][self.kid]['title'] = 'Cafe\u0301'
        basis = knowledge.capture_basis(self.state, self.runtime, [self.kid])
        plan = knowledge.plan_impact(self.state, self.runtime, [self.kid], [])
        self.roundtrip()
        self.assertEqual(self.state['knowledge'][self.kid]['title'], 'Cafe\u0301')
        self.assertTrue(knowledge.validate_basis(basis, self.state, self.runtime)['valid'])
        self.assertEqual(plan, knowledge.plan_impact(self.state, self.runtime, [self.kid], []))
        self.assertNotEqual(knowledge.content_hash({'title': 'Cafe\u0301'}), knowledge.content_hash({'title': 'Caf\u00e9'}))
        self.state['knowledge'][self.kid]['title'] = 'Changed meaning'
        self.assertFalse(knowledge.validate_basis(basis, self.state, self.runtime)['valid'])

    def test_raw_lean_source_hash_and_record_basis_preserve_unicode_distinctions(self):
        formal = self.state['formal_results'][self.state['knowledge'][self.kid]['formal_result_id']]
        formal['lean_code'] = '-- Cafe\u0301\n' + formal['lean_code']
        formal['verification']['source_sha256'] = hashlib.sha256(formal['lean_code'].encode()).hexdigest()
        self.assertTrue(kr.formal_usable(self.state, formal))
        basis = knowledge.capture_basis(self.state, self.runtime, [formal['id']])
        formal['lean_code'] = formal['lean_code'].replace('Cafe\u0301', 'Caf\u00e9')
        self.assertFalse(knowledge.validate_basis(basis, self.state, self.runtime)['valid'])
        self.assertFalse(kr.formal_usable(self.state, formal))

    def test_current_mismatch_has_active_effect_without_positive_knowledge(self):
        aid = self.assessment('mismatch')
        self.roundtrip()  # Baseline must pass sealed-review and storage validation.
        sealed = copy.deepcopy(self.state['identity_assessments'][aid])
        self.state = kr.set_assessment_use(self.state, aid, 'suspended', 'formal objection', 'reviewer')
        self.state = kr.set_assessment_use(self.state, aid, 'active', 'reconfirmed exact mismatch', 'reviewer')
        self.roundtrip()
        self.assertEqual(self.state['identity_assessments'][aid], sealed)
        self.assertTrue(knowledge.assess_use(self.state['identity_assessments'][aid], self.state)['valid'])
        self.assertEqual(kr.usable_links(self.state, self.kid), [])

    def test_qualified_reassessment_restores_negative_and_preserves_sealed_judgment(self):
        aid = self.assessment('mismatch')
        original = copy.deepcopy(self.state['identity_assessments'][aid])
        self.state, self.runtime = knowledge.suspend_assessment_use(self.state, self.runtime, aid,
            reason='Independently identified semantic objection', actor_ref='authorized:review', reason_refs=[original['review_cycle_id']])
        cycle = self.cycle('match', knowledge.assessment_reassessment_proposal(self.state, aid, runtime=self.runtime))
        self.roundtrip()
        self.state, self.runtime = knowledge.apply_assessment_reassessment(self.state, self.runtime, aid,
            cycle['id'], reason='Original negative judgment reaffirmed', actor_ref='authorized:review')
        self.roundtrip()
        use = next(u for u in self.state['assessment_uses'].values() if u['assessment_id'] == aid)
        self.assertEqual(use['status'], 'active')
        self.assertEqual(use['history'][-1]['reassessment_ref'], cycle['id'])
        self.assertEqual(self.state['identity_assessments'][aid], original)
        self.assertEqual(kr.usable_links(self.state, self.kid), [])
        again = knowledge.apply_assessment_reassessment(self.state, self.runtime, aid, cycle['id'],
            reason='Retry', actor_ref='authorized:review')
        self.assertEqual(again, (self.state, self.runtime))

    def test_ordinary_review_cannot_restore_or_withdraw_original_assessment(self):
        aid = self.assessment()
        cycle = self.cycle('mismatch')
        with self.assertRaisesRegex(ValueError, 'reassessment'):
            knowledge.apply_assessment_reassessment(self.state, self.runtime, aid, cycle['id'],
                reason='New ordinary mismatch', actor_ref='authorized:review')

    def test_reassessment_withdrawal_propagates_locally_and_keeps_formal_result(self):
        aid = self.assessment()
        fid = self.state['knowledge'][self.kid]['formal_result_id']
        formal = copy.deepcopy(self.state['formal_results'][fid])
        eid = self.state['identity_assessments'][aid]['execution_ids'][0]
        self.state['goal_judgments'] = [{'id': 'GJ-dependent', 'execution_id': eid, 'basis': 'synthetic:goal',
            'decision': 'supported', 'used_sources': [self.kid], 'current': True},
            {'id': 'GJ-other', 'execution_id': eid, 'basis': 'synthetic:goal', 'decision': 'supported',
             'used_sources': [], 'current': True}]
        cycle = self.cycle('mismatch', knowledge.assessment_reassessment_proposal(self.state, aid, runtime=self.runtime))
        self.state, self.runtime = knowledge.apply_assessment_reassessment(self.state, self.runtime, aid,
            cycle['id'], reason='Original positive judgment was erroneous', actor_ref='authorized:review')
        self.assertEqual(next(u for u in self.state['assessment_uses'].values() if u['assessment_id'] == aid)['status'], 'withdrawn')
        self.assertFalse(self.state['goal_judgments'][0]['current'])
        self.assertTrue(self.state['goal_judgments'][1]['current'])
        self.assertEqual(self.state['formal_results'][fid], formal)
        self.roundtrip()
        current = {g['id']: g['current'] for g in self.state['goal_judgments']}
        self.assertEqual(current, {'GJ-dependent': False, 'GJ-other': True})

    def test_reassessment_rejects_stale_premises_and_original_author(self):
        aid = self.assessment()
        cycle = self.cycle('match', knowledge.assessment_reassessment_proposal(self.state, aid, runtime=self.runtime))
        eid = next(iter(cycle['results'].values()))['execution_id']
        original = self.state['identity_assessments'][aid]['execution_ids'][0]
        self.runtime['executions'][eid]['continuation_of'] = original
        with self.assertRaises(ValueError):
            knowledge.apply_assessment_reassessment(self.state, self.runtime, aid, cycle['id'], reason='Reaffirm', actor_ref='review')
        self.runtime['executions'][eid].pop('continuation_of')
        self.runtime['executions'][eid]['context_origin'] = [original]
        with self.assertRaisesRegex(ValueError, 'author context'):
            knowledge.apply_assessment_reassessment(self.state, self.runtime, aid, cycle['id'], reason='Reaffirm', actor_ref='review')
        self.runtime['executions'][eid]['context_origin'] = []
        self.state['active_trust_environment'] = 'TE-other'
        original_assessment = copy.deepcopy(self.state['identity_assessments'][aid])
        self.state, self.runtime = knowledge.apply_assessment_reassessment(self.state, self.runtime, aid,
            cycle['id'], reason='Reaffirm original judgment with noncurrent premises', actor_ref='review')
        use = next(u for u in self.state['assessment_uses'].values() if u['assessment_id'] == aid)
        self.assertEqual(use['status'], 'suspended')
        self.assertEqual(use['history'][-1]['reassessment_ref'], cycle['id'])
        self.assertEqual(self.state['identity_assessments'][aid], original_assessment)

    def test_inconclusive_reassessment_keeps_suspension_and_has_no_automatic_repeat(self):
        aid = self.assessment('unresolved')
        cycle = self.cycle('unresolved', knowledge.assessment_reassessment_proposal(self.state, aid, runtime=self.runtime))
        self.state, self.runtime = knowledge.apply_assessment_reassessment(self.state, self.runtime, aid,
            cycle['id'], reason='Original uncertainty cannot yet be reassessed', actor_ref='review')
        use = next(u for u in self.state['assessment_uses'].values() if u['assessment_id'] == aid)
        self.assertEqual(use['status'], 'suspended')
        self.assertFalse(any(a.get('review_cycle_id') == cycle['id'] for a in self.runtime['queue']))
        self.roundtrip()

    def test_independent_alternative_link_prevents_unrelated_fallout(self):
        aid = self.assessment()
        alternative = self.assessment()
        self.state['goal_judgments'] = [{'id': 'GJ-dependent', 'used_sources': [self.kid], 'current': True}]
        self.state, self.runtime = knowledge.suspend_assessment_use(self.state, self.runtime, aid,
            reason='Checked objection to first judgment only', actor_ref='review', reason_refs=['checked:objection'])
        self.assertTrue(self.state['goal_judgments'][0]['current'])
        self.assertEqual([l['assessment_id'] for l in kr.usable_links(self.state, self.kid)], [alternative])

    def test_reassessment_rejects_forged_conclusion_and_accepts_final_running_execution(self):
        aid = self.assessment()
        cycle = self.cycle('match', knowledge.assessment_reassessment_proposal(self.state, aid, runtime=self.runtime))
        cycle['decision'] = 'mismatch'
        with self.assertRaisesRegex(ValueError, 'sealed evidence'):
            knowledge.apply_assessment_reassessment(self.state, self.runtime, aid, cycle['id'], reason='Forged', actor_ref='review')
        cycle['decision'] = 'match'
        eid = cycle['results'][cycle['sealed'][-1]]['execution_id']
        execution = self.runtime['executions'][eid]
        execution.update(status='running', outcome=None)
        execution.pop('output')
        self.state, self.runtime = knowledge.apply_assessment_reassessment(self.state, self.runtime, aid,
            cycle['id'], reason='Sealed final response in central transaction', actor_ref='review')
        self.assertTrue(knowledge.assess_use(self.state['identity_assessments'][aid], self.state)['valid'])

    def test_central_explanation_revision_reuses_formal_and_schedules_only_replacement(self):
        from do_math.engine import ResearchEngine, DEFAULT_CONFIG
        from do_math import activities, execution_lifecycle
        from do_math.execution_profiles import build_profiles, profile_ref
        from do_math.repository import new_id
        from unittest.mock import Mock
        self.assessment()
        self.roundtrip()
        original_fid = self.state['knowledge'][self.kid]['formal_result_id']
        original_formal = copy.deepcopy(self.state['formal_results'][original_fid])
        changes = {'summary': 'Clearer summary of the unchanged formal proposition'}
        roots = knowledge.revision_roots(self.state, self.kid, changes)
        impact = knowledge.plan_impact(self.state, self.runtime, roots, [])['computed_impact']
        profiles = build_profiles({**DEFAULT_CONFIG, 'lean_command': ['synthetic-lean']})
        profile = next(p for p in profiles['execution_profiles'].values() if p['role'] == 'research_work')
        self.state['execution_profiles'][profile['id']] = profile
        activity = activities.open_activity(self.runtime, activity_id=new_id('AT'), activity_kind='research_work',
            owner_ref=self.kid, input_refs=[self.kid], opened_at='2026-09-20T00:00:00Z')
        eid, action_id = new_id('EX'), new_id('AC')
        action = {'id': action_id, 'lineage_id': action_id, 'role': 'research_work', 'target': self.kid}
        execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=activity['id'],
            actor_kind='ai', input_manifest={'source': self.kid}, profile_ref=profile_ref(profile), created_at='2026-09-20T00:00:00Z')
        execution.update(role='research_work', action=action, extensions={'knowledge_changes': [
            {'id': self.kid, 'changes': changes, 'impact_set': impact, 'reason': 'Explain the same result'}]})
        activities.assign_execution(self.runtime, activity['id'], execution)
        for status in ('starting', 'running'):
            execution_lifecycle.transition_execution(execution, status, at='2026-09-20T00:00:00Z')
        stale_id = new_id('AC')
        self.runtime['queue'].append({'id': stale_id, 'lineage_id': stale_id, 'role': 'formal_check', 'target': self.kid})
        retained_id = new_id('AC')
        retained = {'id': retained_id, 'lineage_id': retained_id, 'role': 'research_work', 'target': self.kid}
        self.runtime['queue'].append(retained)
        prior_history = copy.deepcopy(self.runtime.get('history', []))
        engine = ResearchEngine.__new__(ResearchEngine)
        engine.instance, engine.runtime = self.state, self.runtime
        engine.head, engine.store = self.head, self.repo
        engine._enqueue = Mock()  # Unrelated planner wake-up; domain follow-up remains real.
        engine._invalidate_goal_currentness = Mock()  # Goal consensus is another owner's consumer.
        execution['input_snapshot'] = self.head
        # Candidate application now owns knowledge revisions; extension-only
        # bundles do not own the separate research response/task disposition.
        bundle = {'integration_id': new_id('IN'), 'payload_sha256': kr.exact_digest(execution['extensions']),
            'members': ['activity-extensions.json/knowledge_changes/0'], 'extensions': execution['extensions'],
            'output': {}, 'owns_response': False, 'impact_set': impact,
            'previous_hashes': {self.kid: knowledge.content_hash(self.state['knowledge'][self.kid])}}
        engine._apply_bundle_candidate(self.state, self.runtime, bundle, action=action, execution_id=eid,
            extensions=execution['extensions'])
        self.state, self.runtime = engine.instance, engine.runtime
        replacements = [k for k in self.state['knowledge'].values() if k.get('supersedes') == self.kid]
        self.assertEqual(len(replacements), 1)
        replacement = replacements[0]
        self.assertEqual(replacement['formal_result_id'], original_fid)
        self.assertEqual(self.state['formal_results'][original_fid], original_formal)
        self.assertFalse(any(a.get('target') == self.kid and a['role'] in {'formal_check', 'identity_review'} for a in self.runtime['queue']))
        self.assertIn(retained, self.runtime['queue'])
        self.assertEqual(self.runtime.get('history', [])[:len(prior_history)], prior_history)
        self.assertEqual([a['role'] for a in self.runtime['queue'] if a.get('target') == replacement['id']], ['identity_review'])
        self.roundtrip()


class KnowledgeReassessmentConnection(unittest.TestCase):
    def test_authorized_replacement_replays_through_domain_publication(self):
        self._publication(replacement=True)

    def test_reaffirmed_noncurrent_judgment_is_recorded_without_restoring_use(self):
        self._publication(replacement=False)

    def _publication(self, *, replacement):
        from test_redesign_REVIEWS import AssessmentReassessmentTests
        from test_review_engine import grant_replacement
        case = AssessmentReassessmentTests()
        case.setUp()
        self.addCleanup(case.doCleanups)
        engine = case.engine
        original = copy.deepcopy(engine.instance['identity_assessments'])
        if replacement:
            grant_replacement(engine)
        else:
            engine.instance['knowledge']['K1']['kind_use_suspended'] = True
        opened = engine._start_assessment_reassessment(**case.request(case.defect()))
        if replacement:
            engine.execute()
            action = engine.pending()
            engine._record_review_recovery(action, ValueError('Exact transcript lost'), retryable=False)
            engine._authorize_review_replacement(action, grant_id='GR-review')
        case.complete()
        cycle = engine.runtime['review_cycles'][opened['review_cycle_id']]
        self.assertEqual(cycle['status'], 'completed')
        self.assertEqual(cycle['decision'], 'match')
        self.assertEqual(case.use()['status'], 'active' if replacement else 'suspended')
        self.assertEqual(engine.instance['identity_assessments'], original)
        self.assertEqual(case.use()['history'][-1]['reassessment_ref'], cycle['id'])
        self.assertEqual(len(cycle.get('replacement_receipts', [])), int(replacement))


class KnowledgeRawSource(unittest.TestCase):
    setUp = KnowledgeAudit2.setUp
    roundtrip = KnowledgeAudit2.roundtrip
    cycle = KnowledgeAudit2.cycle
    assessment = KnowledgeAudit2.assessment

    def test_actual_git_candidate_preserves_exact_source_and_declaration_names(self):
        source = 'theorem \u212a : True := True.intro\n-- e\u0301\r\n'
        data = candidate(); data.update(lean_code=source, declaration_names=['\u212a'])
        self.state, self.runtime, kid = knowledge_io.import_candidate(self.state, self.runtime, data,
            source_ref='raw-source-fixture', actor_ref='raw-source-author')
        record = self.state['knowledge'][kid]
        basis = knowledge.capture_basis(self.state, self.runtime, [record['formal_result_id'], record['exposition_id']])
        impact = knowledge.plan_impact(self.state, self.runtime, [record['formal_result_id']], [])['computed_impact']
        self.roundtrip()
        proposal = kr.proposal_view(self.state, kid)
        self.assertEqual(proposal['lean_code'].encode(), source.encode())
        self.assertEqual(proposal['declaration_names'], ['\u212a'])
        self.assertTrue(knowledge.validate_basis(basis, self.state, self.runtime)['valid'])
        self.assertEqual(knowledge.plan_impact(self.state, self.runtime, [record['formal_result_id']], [])['computed_impact'], impact)
        persisted = self.repo.read_record(record['formal_result_id'], self.head)
        self.assertEqual(persisted['record']['lean_code'].encode(), source.encode())
        physical = self.repo.read(persisted['path'], self.head)
        self.assertEqual(hashlib.sha256(physical).hexdigest(), persisted['sha256'])

    def test_identity_basis_distinguishes_exact_exposition_and_compiler_expressions(self):
        formal = self.state['formal_results'][self.state['knowledge'][self.kid]['formal_result_id']]
        exposition = self.state['expositions'][self.state['knowledge'][self.kid]['exposition_id']]
        exposition['items'][0]['text'] = 'Expression e\u0301'
        first = kr.identity_basis(self.state, self.kid)
        exposition['items'][0]['text'] = 'Expression \u00e9'
        self.assertNotEqual(first, kr.identity_basis(self.state, self.kid))
        formal['verification']['declaration_evidence']['truth']['type'] = 'Expression e\u0301'
        first = kr.identity_basis(self.state, self.kid)
        formal['verification']['declaration_evidence']['truth']['type'] = 'Expression \u00e9'
        self.assertNotEqual(first, kr.identity_basis(self.state, self.kid))

    def test_synthetic_transition_review_cannot_cover_a_changed_unicode_expression(self):
        self.state['trust_environments']['TE-next'] = {**copy.deepcopy(self.state['trust_environments']['TE-test']),
            'id': 'TE-next', 'status': 'registered'}
        transition = knowledge.begin_transition(self.state, 'TE-next')
        result = copy.deepcopy(self.state['formal_results'][self.state['knowledge'][self.kid]['formal_result_id']]['verification'])
        result['id'] = self.kid
        result['declaration_evidence']['truth']['type'] = 'Exact expression \u212a'
        result['identity_review'] = {'decision': 'match', 'result_digest': kr.exact_digest(result),
            'review_ref': 'synthetic:eligible-review', 'policy_ref': 'synthetic:frozen-policy'}
        before = copy.deepcopy(self.state)
        synthetic = knowledge.record_transition_result(self.state, transition, result)
        with self.assertRaisesRegex(ValueError, 'sealed staged identity review runtime'):
            knowledge.activate_transition(self.state, synthetic)
        self.assertEqual(self.state, before)
        result['declaration_evidence']['truth']['type'] = 'Exact expression K'
        invalid = knowledge.record_transition_result(self.state, transition, result)
        with self.assertRaisesRegex(ValueError, 'sealed staged identity review runtime'):
            knowledge.activate_transition(self.state, invalid)
        self.assertEqual(self.state, before)

    def test_actual_git_preserves_exact_compiler_result_and_mathematical_exposition(self):
        formal = self.state['formal_results'][self.state['knowledge'][self.kid]['formal_result_id']]
        formal['lean_code'] += '\n-- e\u0301\r\n'
        formal['verification']['source_sha256'] = hashlib.sha256(formal['lean_code'].encode()).hexdigest()
        formal['verification']['declaration_evidence']['truth']['type'] = 'String.literal "e\u0301"'
        formal['verification']['declaration_signatures'] = {'truth': 'String.literal "e\u0301"'}
        exposition = self.state['expositions'][self.state['knowledge'][self.kid]['exposition_id']]
        exposition['items'][0]['text'] = 'Exact mathematical expression e\u0301'
        expected_formal, expected_exposition = copy.deepcopy(formal), copy.deepcopy(exposition)
        self.roundtrip()
        self.assertEqual(self.state['formal_results'][formal['id']], expected_formal)
        self.assertEqual(self.state['expositions'][exposition['id']], expected_exposition)
        self.assertTrue(kr.formal_usable(self.state, self.state['formal_results'][formal['id']]))

    def test_source_catalog_delivers_exact_proposal_text_and_compiler_keys(self):
        import json
        from do_math.context_store import write_source_catalog
        formal = self.state['formal_results'][self.state['knowledge'][self.kid]['formal_result_id']]
        formal['lean_code'] += '\n-- e\u0301\r\n'
        formal['verification']['declaration_signatures'] = {'\u212a': 'first', 'K': 'second'}
        proposal = kr.proposal_view(self.state, self.kid)
        catalog = write_source_catalog({'proposal': proposal}, self.root)
        row = catalog['entries']['proposal']
        raw = (self.root / row['path']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
        self.assertEqual(json.loads(raw), proposal)

    @category('lean')
    def test_actual_lean_git_revision_and_transition_preserve_exact_inputs_and_evidence(self):
        self._actual_lean_revision_transition(self.roundtrip)

    @category('lean')
    def test_actual_lean_domain_revision_and_transition_preserve_exact_inputs_and_evidence(self):
        self._actual_lean_revision_transition(lambda: None)

    def _actual_lean_revision_transition(self, persist):
        from do_math import formal
        from test_formal import actual_command
        from test_knowledge_import_engine import FormalBoundaryTests
        source = 'theorem \u212a (\u2126 : True) : True := \u2126\r\ntheorem K : True := True.intro\n-- e\u0301\n'
        names = ['\u212a', 'K']
        observed = formal.verify_lean(source=source, declarations=names, workspace=self.root, lean_command=actual_command())
        self.assertEqual(observed['status'], 'verified', observed.get('reason'))
        # Installed compiler; authority adoption and noncompiler clean-build evidence
        # are the same explicit synthetic fixtures as the central boundary tests.
        engine, self.kid = FormalBoundaryTests.host(self, self.root, observed['toolchain'])
        profiles, constraints = self.state['execution_profiles'], self.state['capacity_constraints']
        self.state = engine.instance
        self.state.update(feature_version=5, execution_profiles=profiles, capacity_constraints=constraints)
        self.runtime = {'feature_version': 5, 'queue': [], 'history': []}
        fid = self.state['knowledge'][self.kid]['formal_result_id']
        self.state['formal_results'][fid].update(lean_code=source, declaration_names=names)
        persist()  # The Git case checks candidate transport before compilation.
        proposal = kr.proposal_view(self.state, self.kid)
        self.assertEqual(proposal['lean_code'].encode(), source.encode())
        observed = formal.verify_lean(source=proposal['lean_code'], declarations=proposal['declaration_names'],
            workspace=self.root, lean_command=actual_command(), expected_toolchain=observed['toolchain'])
        self.assertEqual(observed['status'], 'verified', observed.get('reason'))
        self.state = kr.record_formal_result(self.state, self.kid, observed, 'TE-old', runtime=self.runtime)
        expected = copy.deepcopy(self.state['formal_results'][fid])
        persist()
        self.assertEqual(self.state['formal_results'][fid], expected)
        self.assertEqual(self.state['formal_results'][fid]['verification']['source_sha256'], hashlib.sha256(source.encode()).hexdigest())
        changes = {'summary': 'Exact compiler expression \u2126 preserved in a clearer explanation'}
        roots = knowledge.revision_roots(self.state, self.kid, changes)
        scope = knowledge.plan_impact(self.state, self.runtime, roots, [])['computed_impact']
        old = self.kid
        self.state, self.runtime = knowledge.revise_knowledge(self.state, self.runtime, old, changes,
            reason='Explanation only', actor_ref='synthetic:author', declared_impact=scope)
        self.kid = next(k for k, row in self.state['knowledge'].items() if row.get('supersedes') == old)
        persist()
        self.assertEqual(self.state['knowledge'][self.kid]['formal_result_id'], fid)
        self.assertEqual(self.state['formal_results'][fid], expected)
        self.assertEqual(kr.proposal_view(self.state, self.kid)['summary'], changes['summary'])
        self.state['trust_environments']['TE-next'] = {**copy.deepcopy(self.state['trust_environments']['TE-old']),
            'id': 'TE-next', 'status': 'registered', 'source_ref': 'synthetic:next-adoption'}
        transition = knowledge.begin_transition(self.state, 'TE-next')
        transition = knowledge.record_transition_result(self.state, transition, {'id': self.kid, **observed})
        self.runtime['trust_transitions'] = {transition['id']: transition}
        persist()
        stored_transition = self.runtime['trust_transitions'][transition['id']]
        self.assertEqual(stored_transition['results'][self.kid]['declaration_evidence'], observed['declaration_evidence'])
        self.state = knowledge.activate_transition(self.state, stored_transition)
        stored_transition['status'] = 'active'
        persist()
        new_formal = self.state['formal_results'][self.state['knowledge'][self.kid]['formal_result_id']]
        self.assertEqual(new_formal['lean_code'].encode(), source.encode())
        self.assertEqual(new_formal['declaration_names'], names)
        self.assertEqual(new_formal['verification']['declaration_evidence'], observed['declaration_evidence'])
        self.assertEqual(self.state['formal_results'][fid], expected)
        self.assertTrue(kr.formal_usable(self.state, new_formal))


if __name__ == "__main__":
    unittest.main()
