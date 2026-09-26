import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.repository import exact_content_hash

from do_math.review_cycle import (accept_result, authorize_record_replacement, context_for,
                                  next_actions, record_recovery_event, start_review)
from do_math.review_policy import build_review_policy, validate_scope_assessment
from do_math.input_basis import capture_review_input_basis, review_input_basis_changes
from do_math.review_engine import ReviewEngineMixin
from test_review_engine import FakeEngine, grant_replacement


def policy():
    return build_review_policy({
        "id": "RP-identity-v5",
        "version": 5,
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
        "policy_version": 5,
        "required_perspectives": ["formal", "semantic"],
        "initial_slots": [
            {"id": "initial-formal", "perspective": "formal", "required_source_refs": ["proposal"]},
            {"id": "initial-semantic", "perspective": "semantic", "required_source_refs": ["proposal"]},
        ],
        "selected_profile_ref": {"id": "EP-review", "revision": 1, "sha256": "a" * 64},
        "activity_execution_limit": 12,
        "overflow_disposition": "unresolved",
    }


class ReviewRedesignTests(unittest.TestCase):
    def test_missing_v5_scope_opens_an_independent_scope_action_before_initial_reviews(self):
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
        with self.assertRaisesRegex(ValueError, "required perspective"):
            validate_scope_assessment(invalid, policy())

    def test_executed_scope_cannot_merge_initial_and_private_judge_slots(self):
        for reserved in ('scope', 'organize', 'judge-0'):
            with self.subTest(slot=reserved):
                cycle = start_review({'revision': 1}, reviewers=2, policy=policy())
                invalid = assessment()
                invalid['initial_slots'][0]['id'] = reserved
                with self.assertRaisesRegex(ValueError, 'role slot'):
                    accept_result(cycle, next_actions(cycle)[0], {
                        'proposal_digest': cycle['proposal_digest'], 'summary': 'Assess full scope',
                        'used_sources': ['proposal'], 'questions': [], 'scope_complete': True,
                        'scope_assessment': invalid}, 'scope-run')

    def test_scope_added_expertise_requires_an_actual_assigned_slot(self):
        invalid = assessment()
        invalid['required_perspectives'].append('number theory')
        with self.assertRaisesRegex(ValueError, 'required perspective'):
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
        with tempfile.TemporaryDirectory() as root:
            engine = FakeEngine(root)
            grant_replacement(engine)
        approved = authorize_record_replacement(permanent, action, engine.instance, runtime=runtime, grant_id="GR-review")
        self.assertEqual(approved["disposition"], "replacement_ready")
        replacement = approved["action"]
        self.assertTrue(replacement["continuity_broken"])
        self.assertEqual(context_for(approved["cycle"], replacement)["replacement"]["grant_id"], "GR-review")
        with self.assertRaisesRegex(ValueError, "continuity break"):
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

    def test_engine_freezes_adopted_policy_and_scope_at_cycle_opening(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        engine = FakeEngine(self.directory.name)
        engine.instance['config'].update(review_policy=policy(), review_scope_assessment=assessment())
        engine.instance['review_policy'] = policy()
        engine.instance['knowledge']['K1']['owner_activity_id'] = 'ACT-1'
        cycle_id = engine._start_identity_review("K1")
        cycle = engine.runtime["review_cycles"][cycle_id]
        self.assertEqual(cycle["owner_activity_id"], "ACT-1")
        self.assertEqual(cycle["review_input_basis"]["version"], 5)
        self.assertEqual(cycle["reviewer_slots"], ["initial-formal", "initial-semantic"])

    def test_engine_returns_a_structured_slot_recovery_instead_of_reraising_restore_failure(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        engine = FakeEngine(self.directory.name)
        engine.instance['config'].update(review_policy=policy(), review_scope_assessment=assessment())
        engine.instance['review_policy'] = policy()
        engine.instance['knowledge']['K1']['owner_activity_id'] = 'ACT-1'
        cycle_id = engine._start_identity_review("K1")
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


class ReassessmentGitTests(unittest.TestCase):
    def test_actual_split_state_suspend_review_save_reload_and_next_owner(self):
        from test_redesign_KNOWLEDGE import KnowledgeAudit2
        from test_review_cycle import ReviewCycleTests, scoped_start
        from do_math import activities, execution_lifecycle
        from do_math.execution_profiles import profile_ref
        from do_math.repository import new_id
        fixture = KnowledgeAudit2()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        aid = fixture.assessment()
        assessment = fixture.state['identity_assessments'][aid]
        original = fixture.runtime['review_cycles'][assessment['review_cycle_id']]
        original['assessment_id'] = aid
        fixture.state['knowledge'][fixture.kid]['review_cycle_id'] = original['id']
        producer = original['results']['scope:1:scope']['execution_id']
        flawed = original['results']['initial:1:initial-0']['execution_id']
        original['producer_execution_ids'] = [producer]
        fixture.runtime['executions'][flawed]['context_origin'] = [producer]
        fixture.state['review_policy'] = copy.deepcopy(original['review_policy'])
        fixture.state['config'] = {}
        fixture.roundtrip()
        engine = FakeEngine(fixture.root)
        engine.instance, engine.runtime, engine.head, engine.store = fixture.state, fixture.runtime, fixture.head, fixture.repo
        def enqueue(role, target=None, **extra):
            identifier = new_id('AC')
            engine.runtime.setdefault('queue', []).append({'id': identifier, 'lineage_id': identifier,
                'role': role, **({'target': target} if target else {}), **extra})
        engine._enqueue = enqueue
        result = engine._start_assessment_reassessment(aid, exact_content_hash(assessment), {'kind': 'author_context', 'execution_id': flawed})
        fixture.state, fixture.runtime = engine.instance, engine.runtime
        fixture.roundtrip()
        engine.instance, engine.runtime, engine.head = fixture.state, fixture.runtime, fixture.head
        self.assertEqual(next(u for u in engine.instance['assessment_uses'].values() if u['assessment_id'] == aid)['status'], 'suspended')
        while any(a['role'] == 'identity_review' for a in engine.runtime['queue']):
            action = engine.pending()
            cid = action['review_cycle_id']
            cycle = engine.runtime['review_cycles'][cid]
            engine._prepare_review_context(action, fixture.root / 'synthetic-review-input')['context']
            output = ReviewCycleTests().output(cycle, action['stage'])
            if action['stage'] == 'scope':
                scope = scoped_start(cycle['proposal'], reviewers=2, max_rounds=1)['scope_assessment']
                scope.update(policy_id=cycle['review_policy']['id'], policy_version=cycle['review_policy']['version'],
                             selected_profile_ref=profile_ref(fixture.profile), activity_execution_limit=cycle['activity_execution_limit'])
                output.update(scope_complete=True, scope_assessment=scope)
            eid = new_id('EX')
            execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=cycle['owner_activity_id'],
                actor_kind='ai', input_manifest={'proposal_digest': cycle['proposal_digest'], 'prompt': {'sha256': 'a' * 64}},
                profile_ref=profile_ref(fixture.profile), created_at='2026-09-20T00:00:00Z')
            execution.update(role='identity_review', action=copy.deepcopy(action), input_snapshot=engine.head)
            self.assertEqual(engine._admit_review_execution(action, execution)['disposition'], 'admitted')
            activities.assign_execution(engine.runtime, cycle['owner_activity_id'], execution)
            for status in ('starting', 'running'):
                execution_lifecycle.transition_execution(execution, status, at='2026-09-20T00:00:00Z')
            engine.runtime['queue'].remove(action)
            engine._apply_identity_review(action, output, eid)
            execution = engine.runtime['executions'][eid]
            execution.update(output=output, submission_receipt={'state': 'accepted', 'evidence_ref': 'synthetic:review'})
            execution_lifecycle.transition_execution(execution, 'stopping', at='2026-09-20T00:00:00Z', stop_phase='terminating')
            execution_lifecycle.transition_execution(execution, 'ended', at='2026-09-20T00:00:00Z', outcome='output_accepted')
        self.assertEqual(engine._settle_assessment_reassessments(), [result['review_cycle_id']])
        fixture.state, fixture.runtime = engine.instance, engine.runtime
        fixture.roundtrip()
        use = next(u for u in fixture.state['assessment_uses'].values() if u['assessment_id'] == aid)
        self.assertEqual(use['status'], 'active')
        self.assertEqual(use['history'][-1]['reassessment_ref'], result['review_cycle_id'])
        self.assertEqual(fixture.runtime['activities'][result['owner_activity_id']]['followups'][0]['next_owner'], 'research_plan')
        self.assertEqual(fixture.state['identity_assessments'][aid], assessment)


class SealedReplayTests(unittest.TestCase):
    def test_budget_closed_investigation_is_verified_unresolved_not_an_unfinished_vote(self):
        from do_math.review_cycle import start_review, next_actions, defer_for_research, validate_sealed_review
        from test_review_cycle import scoped_start
        scoped = scoped_start({'revision': 1}, reviewers=2)
        cycle = start_review({'revision': 1}, reviewers=2, policy=scoped['review_policy'], scope_assessment=scoped['scope_assessment'])
        cycle['id'] = 'RC-cap'
        action = next_actions(cycle)[0]
        output = {'proposal_digest': cycle['proposal_digest'], 'summary': 'A fixed question remains',
            'used_sources': [], 'questions': [], 'decision': 'unresolved', 'scope_complete': False, 'findings': []}
        requests = [{'id': 'r', 'question': 'Which domain is intended?', 'source_refs': ['proposal']}]
        cycle = defer_for_research(cycle, action, output, requests, 'requester', limit=0)
        runtime = {'executions': {'requester': {'id': 'requester', 'role': 'identity_review', 'status': 'ended',
            'outcome': 'output_accepted', 'output': output, 'action': {**action, 'review_cycle_id': cycle['id']}}}}
        from do_math.engine import DEFAULT_CONFIG
        from do_math.execution_profiles import build_profiles, profile_ref
        config = {**copy.deepcopy(DEFAULT_CONFIG), 'review_research_limit': 0}
        instance = {'config': config, **build_profiles(config)}
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'identity_review')
        runtime['executions']['requester'].update(actor_kind='ai', execution_profile_ref=profile_ref(profile))
        result = validate_sealed_review(cycle, runtime, instance=instance)
        self.assertEqual((result['status'], result['decision']), ('unresolved', 'unresolved'))
        instance['config']['review_research_limit'] = 3
        with self.assertRaisesRegex(ValueError, 'closure|limit'):
            validate_sealed_review(cycle, runtime, instance=instance)

    def test_authorized_replacement_keeps_full_authority_and_sealed_input(self):
        from do_math.review_cycle import validate_sealed_review, record_recovery_event
        with tempfile.TemporaryDirectory() as directory:
            engine = FakeEngine(directory)
            grant_replacement(engine)
            cid = engine._start_identity_review('K1')
            action = engine.pending()
            cycle = engine.runtime['review_cycles'][cid]
            short = {k: action[k] for k in ('stage', 'slot', 'round')}
            engine.runtime['review_cycles'][cid] = record_recovery_event(cycle, short,
                {'reason': 'lost exact public transcript', 'retryable': False, 'preserved_range': {'slot': action['slot']}})
            engine._authorize_review_replacement(action, grant_id='GR-review')
            while any(a['role'] == 'identity_review' for a in engine.runtime['queue']):
                engine.execute()
            cycle = engine.runtime['review_cycles'][cid]
            self.assertIn('sealed_input_sha256', cycle['replacement_receipts'][0]['authorization'])
            self.assertEqual(validate_sealed_review(cycle, engine.runtime, instance=engine.instance)['decision'], 'match')
            cycle['replacement_receipts'][0]['authorization']['sealed_input_sha256'] = 'changed'
            with self.assertRaisesRegex(ValueError, 'sealed input changed'):
                validate_sealed_review(cycle, engine.runtime, instance=engine.instance)

    def test_previous_review_must_resolve_to_its_actual_preserved_cycle(self):
        from do_math.review_cycle import start_review, accept_result, next_actions, validate_sealed_review
        from test_review_cycle import scoped_start, ReviewCycleTests
        runtime = {'executions': {}, 'review_cycles': {}}
        previous = None
        for revision in (1, 2):
            seed = scoped_start({'revision': revision}, reviewers=2)
            cycle = start_review({'revision': revision}, reviewers=2, previous=previous,
                policy=seed['review_policy'], scope_assessment=seed['scope_assessment'])
            cid = 'cycle-' + str(revision)
            cycle['id'] = cid
            while next_actions(cycle):
                action = next_actions(cycle)[0]
                output = ReviewCycleTests().output(cycle, action['stage'])
                eid = cid + ':' + action['slot']
                runtime['executions'][eid] = {'id': eid, 'role': 'identity_review', 'status': 'ended',
                    'outcome': 'output_accepted', 'output': output, 'action': {**action, 'review_cycle_id': cid}}
                cycle = accept_result(cycle, action, output, eid)
            runtime['review_cycles'][cid] = cycle
            previous = cycle
        self.assertEqual(validate_sealed_review(cycle, runtime)['decision'], 'match')
        forged = copy.deepcopy(cycle)
        next(iter(forged['results'].values()))['stage'] = 'judge'
        with self.assertRaisesRegex(ValueError, 'sealed evidence'):
            validate_sealed_review(forged, runtime)
        del runtime['review_cycles']['cycle-1']
        with self.assertRaisesRegex(ValueError, 'preserved cycle'):
            validate_sealed_review(cycle, runtime)

    def test_fixed_private_research_is_replayed_before_requesters_final_vote(self):
        from do_math.review_cycle import accept_research_result, accept_result, next_actions, validate_sealed_review
        from test_review_research import PureResearchTests
        from test_review_cycle import ReviewCycleTests
        fixture = PureResearchTests()
        cycle, action = fixture.fixture()
        cycle['id'] = 'RC-research'
        provisional = cycle['turns'][action['slot']][0]['content']['provisional_result']
        rid = next(iter(cycle['research']))
        answer = fixture.result(cycle)
        runtime = {'executions': {
            'requester': {'id': 'requester', 'role': 'identity_review', 'status': 'ended', 'outcome': 'output_accepted',
                          'output': provisional, 'action': {**action, 'review_cycle_id': cycle['id']}},
            'investigator': {'id': 'investigator', 'role': 'supplemental_research', 'status': 'ended', 'outcome': 'output_accepted',
                             'output': answer, 'action': {'role': 'supplemental_research', 'research_request_id': rid, 'review_cycle_id': cycle['id']}}
        }}
        cycle = accept_research_result(cycle, rid, answer, 'investigator')
        while next_actions(cycle):
            pending = next_actions(cycle)[0]
            output = ReviewCycleTests().output(cycle, pending['stage'])
            eid = pending['slot']
            runtime['executions'][eid] = {'id': eid, 'role': 'identity_review', 'status': 'ended', 'outcome': 'output_accepted',
                'output': output, 'action': {**pending, 'review_cycle_id': cycle['id']}}
            cycle = accept_result(cycle, pending, output, eid)
        self.assertEqual(validate_sealed_review(cycle, runtime)['decision'], 'match')
        runtime['executions']['investigator']['output']['request_digest'] = 'forged'
        with self.assertRaisesRegex(ValueError, 'actual accepted execution'):
            validate_sealed_review(cycle, runtime)


class AssessmentReassessmentTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.engine = FakeEngine(self.directory.name)
        self.engine.instance['config'].pop('review_scope_assessment')
        self.original = self.engine._start_identity_review('K1')
        while any(a['role'] == 'identity_review' for a in self.engine.runtime['queue']):
            self.engine.execute()
        self.assessment = self.engine.assessment()

    def request(self, evidence):
        return {'assessment_id': self.assessment['id'], 'assessment_sha256': exact_content_hash(self.assessment),
                'evidence': evidence}

    def defect(self):
        cycle = self.engine.runtime['review_cycles'][self.original]
        execution_id = cycle['results']['initial:1:initial-0']['execution_id']
        self.engine.runtime['executions'][execution_id]['context_origin'] = ['author']
        self.engine.runtime['executions']['author'] = {'id': 'author', 'status': 'ended'}
        return {'kind': 'author_context', 'execution_id': execution_id}

    def use(self):
        return next(row for row in self.engine.instance['assessment_uses'].values()
                    if row['assessment_id'] == self.assessment['id'])

    def complete(self, decision='match'):
        while any(a['role'] == 'identity_review' for a in self.engine.runtime['queue']):
            action = self.engine.pending()
            cycle = self.engine.runtime['review_cycles'][action['review_cycle_id']]
            changes = {}
            if action['stage'] == 'initial' and decision == 'unresolved':
                changes = {'decision': 'unresolved', 'scope_complete': False}
            elif action['stage'] == 'initial' and action['slot'] == 'initial-0' and decision == 'mismatch':
                changes = {'decision': 'mismatch', 'findings': [{'id': 'defect', 'statement': 'The stated domain differs', 'evidence': ['proposal']}]}
            elif action['stage'] == 'judge' and decision == 'mismatch':
                changes = {'decision': 'mismatch', 'issue_verdicts': [dict(issue_id=i, decision='approved', reason='Exact mismatch confirmed', evidence=['proposal']) for i in cycle['issues']]}
            self.engine.execute(changes)

    def test_confirmed_error_withdraws_without_creating_a_new_identity_assessment(self):
        self.engine.instance['goal_judgments'] = [
            {'id': 'GJ-dependent', 'used_sources': ['K1'], 'current': True},
            {'id': 'GJ-unrelated', 'used_sources': [], 'current': True}]
        formal = copy.deepcopy(self.engine.instance['formal_results'])
        self.engine._start_assessment_reassessment(**self.request(self.defect()))
        self.complete('mismatch')
        self.assertEqual(self.use()['status'], 'withdrawn')
        self.assertEqual(len(self.engine.instance['identity_assessments']), 1)
        self.assertFalse(self.engine.usable())
        self.assertFalse(self.engine.instance['goal_judgments'][0]['current'])
        self.assertTrue(self.engine.instance['goal_judgments'][1]['current'])
        self.assertEqual(self.engine.instance['formal_results'], formal)

    def test_reassessment_organizer_answer_and_judges_replay_the_same_sealed_object(self):
        from do_math.review_cycle import validate_sealed_review
        result = self.engine._start_assessment_reassessment(**self.request(self.defect()))
        self.engine.execute()  # scope
        self.engine.execute({'decision': 'mismatch', 'findings': [
            {'id': 'disputed', 'statement': 'An input premise may be missing', 'evidence': ['proposal']}]})
        stages = []
        while any(a['role'] == 'identity_review' for a in self.engine.runtime['queue']):
            stages.append(self.engine.pending()['stage'])
            self.engine.execute()
        self.assertIn('organize', stages)
        self.assertIn('answer', stages)
        self.assertEqual(stages.count('judge'), 6)
        cycle = self.engine.runtime['review_cycles'][result['review_cycle_id']]
        self.assertEqual(validate_sealed_review(cycle, self.engine.runtime, instance=self.engine.instance)['decision'], 'match')
        self.assertEqual(self.use()['status'], 'active')

    def test_unresolved_remains_suspended_and_finite_activity_retains_next_owner(self):
        result = self.engine._start_assessment_reassessment(**self.request(self.defect()))
        self.complete('unresolved')
        self.assertEqual(self.use()['status'], 'suspended')
        self.assertEqual(self.engine._settle_assessment_reassessments(), [result['review_cycle_id']])
        activity = self.engine.runtime['activities'][result['owner_activity_id']]
        self.assertEqual(activity['status'], 'finished')
        self.assertEqual(activity['unresolved'][0]['next_owner'], 'research_plan')
        self.assertTrue(activity['unresolved'][0]['revisit_conditions'])
        repeated = self.engine._start_assessment_reassessment(**self.request(self.defect()))
        self.assertEqual(repeated['disposition'], 'already_reviewed')

    def test_reaffirmed_negative_original_is_not_positive_knowledge(self):
        self.engine = FakeEngine(self.directory.name, rounds=1)
        self.engine.instance['config'].pop('review_scope_assessment')
        self.original = self.engine._start_identity_review('K1')
        self.complete('mismatch')
        self.assessment = self.engine.assessment()
        self.assertEqual(self.assessment['decision'], 'mismatch')
        self.engine._start_assessment_reassessment(**self.request(self.defect()))
        self.complete('match')
        self.assertEqual(self.use()['status'], 'active')
        self.assertFalse(self.engine.usable())
        self.assertEqual(self.engine.assessment()['decision'], 'mismatch')

    def test_changed_current_input_and_forged_result_target_are_rejected(self):
        from do_math.review_cycle import validate_sealed_review
        result = self.engine._start_assessment_reassessment(**self.request(self.defect()))
        premises = copy.deepcopy(self.engine.instance['review_policy'])
        self.engine.instance['review_policy']['activity_execution_limit'] += 1
        with self.assertRaisesRegex(ValueError, 'premises changed'):
            self.engine._review_cycle(self.engine.pending())
        self.engine.instance['review_policy'] = premises
        self.engine.instance['knowledge']['K1']['kind_use_suspended'] = True
        with self.assertRaisesRegex(ValueError, 'premises changed'):
            self.engine._review_cycle(self.engine.pending())
        self.engine.instance['knowledge']['K1'].pop('kind_use_suspended')
        self.complete()
        cycle = copy.deepcopy(self.engine.runtime['review_cycles'][result['review_cycle_id']])
        entry = next(iter(cycle['results'].values()))
        entry['output']['proposal_digest'] = 'another-target'
        with self.assertRaisesRegex(ValueError, 'actual accepted execution|another proposal'):
            validate_sealed_review(cycle, self.engine.runtime, instance=self.engine.instance)

    def test_ordinary_report_does_not_suspend(self):
        result = self.engine._start_assessment_reassessment(**self.request({'kind': 'report', 'text': 'It seems wrong'}))
        self.assertEqual(result['disposition'], 'report_only')
        self.assertEqual(self.use()['status'], 'active')

    def test_actual_central_control_and_activity_settlement_call_the_reassessment_mixin(self):
        from do_math.engine import ResearchEngine
        request = {'id': 'CTRL-reassessment', 'action': 'request',
                   'config': {'role': 'identity_review', 'assessment_reassessment': self.request(self.defect())}}
        self.assertTrue(ResearchEngine._review_recovery_control(self.engine, request))
        cid = self.engine.pending()['review_cycle_id']
        self.complete('unresolved')
        cycle = self.engine.runtime['review_cycles'][cid]
        eid = list(cycle['results'].values())[-1]['execution_id']
        ResearchEngine._settle_activity(self.engine, eid)
        activity = self.engine.runtime['activities'][cycle['owner_activity_id']]
        self.assertEqual(activity['status'], 'finished')
        self.assertEqual(activity['unresolved'][0]['next_owner'], 'research_plan')

    def test_independent_objection_must_have_read_the_exact_original_assessment(self):
        from do_math.review_cycle import start_review, accept_result, next_actions
        from test_review_cycle import ReviewCycleTests, scoped_start
        for bound in (False, True):
            proposal = {'revision': 1, **({'original_assessment': copy.deepcopy(self.assessment)} if bound else {})}
            seed = scoped_start(proposal, reviewers=2, max_rounds=1)
            cycle = start_review(proposal, reviewers=2, policy=seed['review_policy'])
            cid = 'objection-' + str(bound)
            cycle['id'] = cid
            while next_actions(cycle):
                action = next_actions(cycle)[0]
                output = ReviewCycleTests().output(cycle, action['stage'])
                if action['stage'] == 'scope':
                    output.update(scope_complete=True, scope_assessment=seed['scope_assessment'])
                elif action['stage'] == 'initial' and action['slot'] == 'initial-0':
                    output.update(decision='mismatch', findings=[{'id': 'specific', 'statement': 'The original domain judgment conflicts with its input',
                        'evidence': ['assessment:' + self.assessment['id']]}])
                eid = cid + '-' + action['stage'] + '-' + action['slot']
                self.engine.runtime['executions'][eid] = {'id': eid, 'role': 'identity_review', 'status': 'ended',
                    'actor_kind': 'ai', 'execution_profile_ref': copy.deepcopy(self.engine.profile),
                    'outcome': 'output_accepted', 'output': copy.deepcopy(output), 'action': {**action, 'review_cycle_id': cid}}
                cycle = accept_result(cycle, action, output, eid)
            self.engine.runtime['review_cycles'][cid] = cycle
            result = self.engine._start_assessment_reassessment(**self.request({'kind': 'independent_objection',
                'review_cycle_id': cid, 'result_key': 'initial:1:initial-0', 'finding_id': 'specific'}))
            self.assertEqual(result['disposition'], 'reassessment_opened' if bound else 'report_only')

    def test_actual_scope_to_sealed_reaffirmation_restores_same_assessment(self):
        from do_math.review_cycle import validate_sealed_review
        result = self.engine._start_assessment_reassessment(**self.request(self.defect()))
        cid = result['review_cycle_id']
        self.assertEqual(self.use()['status'], 'suspended')
        self.assertEqual(self.engine.pending()['stage'], 'scope')
        self.assertEqual(self.engine.instance['knowledge']['K1']['review_cycle_id'], self.original)
        while any(a['role'] == 'identity_review' for a in self.engine.runtime['queue']):
            self.engine.execute()
        cycle = self.engine.runtime['review_cycles'][cid]
        self.assertEqual(validate_sealed_review(cycle, self.engine.runtime, instance=self.engine.instance)['decision'], 'match')
        self.assertEqual(self.use()['status'], 'active')
        self.assertEqual(len(self.engine.instance['identity_assessments']), 1)
        self.assertEqual(self.engine.instance['identity_assessments'][self.assessment['id']], self.assessment)
        self.assertEqual(self.use()['history'][-1]['reassessment_ref'], cid)
        execution_id = next(iter(cycle['results'].values()))['execution_id']
        profile_id = self.engine.runtime['executions'][execution_id]['execution_profile_ref']['id']
        del self.engine.instance['execution_profiles'][profile_id]
        with self.assertRaisesRegex(ValueError, 'profile'):
            validate_sealed_review(cycle, self.engine.runtime, instance=self.engine.instance)

    def test_stale_original_and_unconfirmed_defect_do_not_suspend(self):
        with self.assertRaisesRegex(ValueError, 'exact original'):
            request = self.request(self.defect())
            request['assessment_sha256'] = 'stale'
            self.engine._start_assessment_reassessment(**request)
        eid = self.assessment['execution_ids'][-1]
        result = self.engine._start_assessment_reassessment(**self.request({'kind': 'author_context', 'execution_id': eid}))
        self.assertEqual(result['disposition'], 'report_only')
        self.assertEqual(self.use()['status'], 'active')

    def test_incomplete_and_original_author_continuation_are_rejected(self):
        from do_math.review_cycle import validate_sealed_review
        result = self.engine._start_assessment_reassessment(**self.request(self.defect()))
        cycle = self.engine.runtime['review_cycles'][result['review_cycle_id']]
        with self.assertRaisesRegex(ValueError, 'complete|sealed'):
            validate_sealed_review(cycle, self.engine.runtime, instance=self.engine.instance)
        execution = {'id': 'forbidden-continuation', 'actor_kind': 'ai', 'owner_activity_id': result['owner_activity_id'],
                     'status': 'queued', 'continuation_of': self.assessment['execution_ids'][0]}
        with self.assertRaisesRegex(ValueError, 'author|independent'):
            self.engine._admit_review_execution(self.engine.pending(), execution)
        while any(a['role'] == 'identity_review' for a in self.engine.runtime['queue']):
            self.engine.execute()
        cycle = self.engine.runtime['review_cycles'][result['review_cycle_id']]
        eid = next(iter(cycle['results'].values()))['execution_id']
        self.engine.runtime['executions'][eid]['continuation_of'] = self.assessment['execution_ids'][0]
        with self.assertRaisesRegex(ValueError, 'author|independent'):
            validate_sealed_review(cycle, self.engine.runtime, instance=self.engine.instance)


if __name__ == "__main__":
    unittest.main()
