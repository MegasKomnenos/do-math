"""Review policy and scope (``review_policy``, ``review_cycle``, ``input_basis``; layer 1, and the ``review_engine`` mixin, layer 2).

The scope stage, the required perspectives and slots, and the inputs each
review stage is frozen to. The pure tests call the policy and cycle functions
directly; the engine tests run the product's ``ResearchEngine`` over the stored
review state of ``support.review_scene`` (candidate theorem ``K1``, verified
formal evidence) and call the mixin as the owner does. Moved from
``test_review_policy`` (``ReviewScopeTests``), whose engine tests ran on
``review_fixtures.ReviewFakeEngine`` (no repository, ``_save`` an autospec
double, a store that read no artifact).
"""
import copy
from pathlib import Path
import re
import tempfile
import unittest

from do_math.input_basis import capture_review_input_basis, review_input_basis_changes
from do_math.review_cycle import (accept_result, authorize_record_replacement, context_for,
                                  next_actions, record_recovery_event, start_review)
from do_math.review_policy import build_review_policy, minimum_scope_executions, validate_scope_assessment
from review_fixtures import grant_replacement
from support.review_scene import ReviewScene, warm


def setUpModule():
    warm()


def policy():
    return build_review_policy({
        "id": "RP-identity-v5",
        "required_perspectives": ["formal", "semantic"],
        "minimum_initial_slots": 2,
        "judge_slots": ["judge-0", "judge-1", "judge-2"],
        "round_limit": 2,
        "activity_execution_limit": 12,
        "overflow_disposition": "unresolved",
    })


def assessment():
    return {
        "assessment_id": "SA-1",
        "policy_id": "RP-identity-v5",
        "required_perspectives": ["formal", "semantic"],
        "initial_slots": [
            {"id": "initial-formal", "perspective": "formal", "required_source_refs": ["proposal"]},
            {"id": "initial-semantic", "perspective": "semantic", "required_source_refs": ["proposal"]},
        ],
        "selected_profile_ref": {"id": "EP-review", "revision": 1, "sha256": "a" * 64},
        "activity_execution_limit": 12,
        "overflow_disposition": "unresolved",
    }


class ReviewScopeTests(unittest.TestCase):
    def test_missing_scope_opens_an_independent_scope_action_before_initial_reviews(self):
        cycle = start_review({"revision": "r1"}, reviewers=2, policy=policy())
        self.assertEqual(cycle["phase"], "scope")
        scope_action = next_actions(cycle)
        self.assertEqual(scope_action, [{"stage": "scope", "slot": "scope", "round": 1}])
        output = {"proposal_digest": cycle["proposal_digest"], "summary": "Need formal and semantic review.",
                  "used_sources": ["proposal"], "questions": [], "scope_complete": True,
                  "scope_assessment": assessment()}
        scoped = accept_result(cycle, scope_action[0], output, "scope-execution")
        self.assertEqual(scoped["phase"], "initial")
        self.assertEqual([action["slot"] for action in next_actions(scoped)], ["initial-formal", "initial-semantic"])

    def test_scope_then_initial_organization_and_independent_judgment_use_only_sealed_stages(self):
        cycle = start_review({"revision": "r1"}, reviewers=2, policy=policy())
        scope = next_actions(cycle)[0]
        cycle = accept_result(cycle, scope, {
            "proposal_digest": cycle["proposal_digest"], "summary": "Two perspectives are required.",
            "used_sources": ["proposal"], "questions": [], "scope_complete": True,
            "scope_assessment": assessment(),
        }, "scope-run")
        for action in list(next_actions(cycle)):
            finding = {"id": action["slot"] + "-finding", "statement": "The proposal is incomplete.",
                       "evidence": ["proposal"]}
            cycle = accept_result(cycle, action, {
                "proposal_digest": cycle["proposal_digest"], "summary": "A material mismatch exists.",
                "used_sources": ["proposal"], "questions": [], "decision": "mismatch",
                "scope_complete": True, "findings": [finding],
            }, action["slot"] + "-run")
        organize = next_actions(cycle)[0]
        self.assertEqual(organize["stage"], "organize")
        finding_refs = [entry["ref"] for entry in cycle["findings"].values()]
        cycle = accept_result(cycle, organize, {
            "proposal_digest": cycle["proposal_digest"], "summary": "Each finding remains a separate issue.",
            "used_sources": ["proposal"], "questions": [],
            "issues": [{"id": "issue-" + ref["slot"], "finding_refs": [ref],
                        "answer_role_slot_id": ref["slot"]} for ref in finding_refs],
        }, "organize-run")
        judges = next_actions(cycle)
        self.assertEqual({action["stage"] for action in judges}, {"judge"})
        self.assertTrue(all(context_for(cycle, action)["completed_results"] for action in judges))
        for action in judges:
            cycle = accept_result(cycle, action, {
                "proposal_digest": cycle["proposal_digest"], "summary": "The objections are established.",
                "used_sources": ["proposal"], "questions": [], "decision": "mismatch",
                "scope_complete": True, "new_findings": [],
                "issue_verdicts": [{"issue_id": issue_id, "decision": "approved",
                                    "reason": "The evidence identifies the mismatch.", "evidence": ["proposal"]}
                                   for issue_id in cycle["issues"]],
            }, action["slot"] + "-run")
        self.assertEqual((cycle["status"], cycle["decision"]), ("completed", "mismatch"))

    def test_scope_assessment_freezes_required_slots_profile_and_activity_budget(self):
        cycle = start_review({"revision": "r1"}, reviewers=2, policy=policy(), scope_assessment=assessment())
        self.assertEqual(cycle["reviewer_slots"], ["initial-formal", "initial-semantic"])
        self.assertEqual(cycle["review_policy"]["id"], "RP-identity-v5")
        self.assertEqual(cycle["scope_assessment"]["selected_profile_ref"]["id"], "EP-review")
        self.assertEqual(cycle["activity_execution_limit"], 12)
        self.assertEqual(cycle["required_source_refs"], ["proposal"])
        self.assertEqual({action["slot"] for action in next_actions(cycle)}, {"initial-formal", "initial-semantic"})

    def test_scope_assessment_rejects_missing_required_perspective(self):
        invalid = copy.deepcopy(assessment())
        invalid["required_perspectives"] = ["formal"]
        with self.assertRaisesRegex(ValueError, "^scope assessment omits a required perspective$"):
            validate_scope_assessment(invalid, policy())

    def test_executed_scope_cannot_merge_initial_and_private_judge_slots(self):
        for reserved in ('scope', 'organize', 'judge-0'):
            with self.subTest(slot=reserved):
                cycle = start_review({'revision': 1}, reviewers=2, policy=policy())
                invalid = assessment()
                invalid['initial_slots'][0]['id'] = reserved
                with self.assertRaisesRegex(ValueError, '^scope assessment reuses an independent role slot$'):
                    accept_result(cycle, next_actions(cycle)[0], {
                        'proposal_digest': cycle['proposal_digest'], 'summary': 'Assess full scope',
                        'used_sources': ['proposal'], 'questions': [], 'scope_complete': True,
                        'scope_assessment': invalid}, 'scope-run')

    def test_scope_assessment_rejects_a_blank_text_as_the_scope_wire_does(self):
        invalid = assessment()
        invalid['initial_slots'][0]['perspective'] = '   '
        with self.assertRaisesRegex(ValueError, 'scope_assessment/initial_slots/0/perspective'):
            validate_scope_assessment(invalid, policy())

    def test_scope_added_expertise_requires_an_actual_assigned_slot(self):
        invalid = assessment()
        invalid['required_perspectives'].append('number theory')
        with self.assertRaisesRegex(ValueError, '^scope assessment has no slot for a required perspective$'):
            validate_scope_assessment(invalid, policy())

    def test_permanent_restoration_loss_blocks_its_slot_until_a_current_grant_authorizes_a_replacement(self):
        cycle = start_review({"revision": "r1"}, reviewers=2, policy=policy(), scope_assessment=assessment())
        action = next_actions(cycle)[0]
        retryable = record_recovery_event(cycle, action, {
            "reason": "source_read_error", "retryable": True, "preserved_range": {"slot": action["slot"], "through_index": 1},
        })
        self.assertEqual(retryable["status"], "working")
        self.assertEqual(next_actions(retryable), [action, next_actions(cycle)[1]])
        permanent = record_recovery_event(retryable, action, {
            "reason": "permanent_loss", "retryable": False, "preserved_range": {"slot": action["slot"], "through_index": 1},
        })
        self.assertEqual((permanent["status"], permanent["decision"]), ("working", None))
        self.assertEqual(permanent["continuity_events"][-1]["reason"], "permanent_loss")
        self.assertTrue(permanent["continuity_events"][-1]["continuity_broken"])
        self.assertEqual([pending["slot"] for pending in next_actions(permanent)], ["initial-semantic"])
        permanent.update(id='RC-test', knowledge_id='K1')
        runtime = {'executions': {}, 'review_cycles': {'RC-test': permanent}}
        denied = authorize_record_replacement(permanent, action, {"grants": {}}, runtime=runtime)
        self.assertEqual(denied["disposition"], "authorization_denied")
        # The grant is the one the product's governance applies to an instance holding K1.
        with tempfile.TemporaryDirectory() as root:
            engine = ReviewScene(root).engine
            grant_replacement(engine)
        approved = authorize_record_replacement(permanent, action, engine.instance, runtime=runtime, grant_id="GR-review")
        self.assertEqual(approved["disposition"], "replacement_ready")
        replacement = approved["action"]
        self.assertTrue(replacement["continuity_broken"])
        self.assertEqual(context_for(approved["cycle"], replacement)["replacement"]["grant_id"], "GR-review")
        with self.assertRaisesRegex(ValueError, "^replacement input manifest omits its continuity break$"):
            accept_result(approved["cycle"], replacement, {
                "proposal_digest": approved["cycle"]["proposal_digest"], "summary": "The review found a mismatch.",
                "used_sources": ["proposal"], "questions": [], "decision": "mismatch",
                "scope_complete": True, "findings": [{"id": "replacement-finding", "statement": "A mismatch remains.", "evidence": ["proposal"]}],
            }, "replacement-run")
        accepted = accept_result(approved["cycle"], replacement, {
            "proposal_digest": approved["cycle"]["proposal_digest"], "summary": "The review found a mismatch.",
            "used_sources": ["proposal"], "questions": [], "decision": "mismatch",
            "scope_complete": True, "findings": [{"id": "replacement-finding", "statement": "A mismatch remains.", "evidence": ["proposal"]}],
        }, "replacement-run", {"replacement_for": replacement["replacement_for"], "grant_id": "GR-review",
                               "grant_sha256": replacement["grant_sha256"]})
        self.assertEqual(accepted["replacement_receipts"][-1]["execution_id"], "replacement-run")

    def test_review_input_basis_detects_policy_scope_and_profile_drift(self):
        cycle = start_review({"revision": "r1"}, reviewers=2, policy=policy(), scope_assessment=assessment())
        basis = capture_review_input_basis(cycle)
        self.assertEqual(review_input_basis_changes(basis, cycle), [])
        changed = copy.deepcopy(cycle)
        changed["scope_assessment"]["selected_profile_ref"]["revision"] = 2
        self.assertEqual(review_input_basis_changes(basis, changed)[0]["field"], "selected_profile_ref")

    def test_scope_execution_minimum_in_the_review_contract_matches_the_policy(self):
        """The documented U+N+4 and U+2N+7 lower bounds are the function the checks run."""
        text = (Path(__file__).resolve().parents[3] / '계약' / '동일성-검토.md').read_text(encoding='utf-8')
        formulas = {}
        for label, rounds in (('한 회차의 하한은', (1,)), ('두 회차 이상의 하한은', (2, 3, 5))):
            match = re.search(re.escape(label) + r' U\+(\d*)N\+(\d+)', text)
            self.assertIsNotNone(match, label)
            formulas[rounds] = (int(match.group(1) or 1), int(match.group(2)))
        for rounds, (per_slot, fixed) in formulas.items():
            for round_limit in rounds:
                for used in (0, 2):
                    for slots in (1, 3):
                        self.assertEqual(minimum_scope_executions(slots, round_limit, used),
                                         used + per_slot * slots + fixed, (round_limit, used, slots))


class EngineScopeTests(unittest.TestCase):
    """The engine's review mixin over the stored review state (``support.review_scene``)."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.scene = ReviewScene(temporary.name)
        self.engine = self.scene.engine

    def test_engine_freezes_adopted_policy_and_opens_every_review_at_its_scope_stage(self):
        engine = self.engine
        engine.instance['review_policy'] = policy()
        cycle_id = engine._start_identity_review("K1")
        cycle = engine.runtime["review_cycles"][cycle_id]
        self.assertEqual(cycle["review_policy"], policy())
        self.assertEqual((cycle["phase"], cycle["scope_assessment"], cycle["owner_activity_id"]), ("scope", None, None))
        self.assertEqual(cycle["review_input_basis"]["values"]["review_policy"], policy())
        self.assertEqual([(action["stage"], action["slot"]) for action in engine.runtime["queue"]], [("scope", "scope")])

    def test_engine_returns_a_structured_slot_recovery_instead_of_reraising_restore_failure(self):
        engine = self.engine
        engine.instance['review_policy'] = policy()
        cycle_id = self.scene.start("K1", scope=assessment())
        action = next(item for item in engine.runtime["queue"] if item["role"] == "identity_review")
        cycle = engine.runtime["review_cycles"][cycle_id]
        cycle["turns"][action["slot"]] = [{"role": "user", "content": "lost", "message_id": "lost"}]
        cycle["transcript_manifest"][action["slot"]] = [{"sha256": "wrong", "bytes": 4, "proposal_digest": cycle["proposal_digest"], "index": 0, "ref": "lost"}]
        with tempfile.TemporaryDirectory() as directory:
            outcome = engine._prepare_review_context(action, Path(directory))
        self.assertEqual(outcome["disposition"], "recovery_recorded")
        self.assertEqual(outcome["recovery"]["disposition"], "replacement_authorization_required")
        self.assertFalse(outcome['recovery']['recovery_event']['retryable'])
        self.assertEqual(engine.runtime["review_cycles"][cycle_id]["status"], "working")


if __name__ == "__main__":
    unittest.main()
