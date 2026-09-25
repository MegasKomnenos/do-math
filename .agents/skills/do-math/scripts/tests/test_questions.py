from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import questions
from do_math.question_engine import QuestionEngineMixin


class QuestionTests(unittest.TestCase):
    def setUp(self):
        self.instance = {"id": "I", "knowledge": {}}
        self.runtime = {"tasks": {"A": {"id": "A"}, "B": {"id": "B"}}, "question_links": []}
        self.a = questions.link(self.runtime, execution_id="E1", field="output/questions/0", owner="user", targets=["A"], blocks=True)
        self.b = questions.link(self.runtime, execution_id="E2", field="output/questions/0", owner="user", targets=["B"], blocks=True)

    def test_only_the_explicitly_affected_task_waits_and_plan_can_choose_other_tasks(self):
        self.assertEqual(len(questions.user_waits({"role": "research_work", "target": "A"}, self.instance, self.runtime)), 1)
        self.assertEqual(questions.user_waits({"role": "research_work", "target": "C"}, self.instance, self.runtime), [])
        self.assertEqual(questions.user_waits({"role": "research_plan"}, self.instance, self.runtime), [])
        questions.link(self.runtime, execution_id="E3", field="output/questions/0", owner="user", targets=["I"], blocks=True)
        self.assertTrue(questions.user_waits({"role": "research_plan"}, self.instance, self.runtime))
        self.assertFalse(questions.user_waits({"role": "intent_interpretation"}, self.instance, self.runtime))

    def test_resolving_one_user_question_preserves_the_other(self):
        questions.resolve_user(self.runtime, [self.a["id"]], resolution_ref="D", affected_ids=["A"])
        self.assertEqual(self.a["status"], "resolved")
        self.assertEqual(self.b["status"], "open")
        with self.assertRaises(ValueError):
            questions.resolve_user(self.runtime, [self.b["id"]], resolution_ref="unrelated", affected_ids=["A"])

    def test_an_ai_extension_cannot_resolve_a_user_question(self):
        context = {"instance_id": "I", "action": {"role": "research_plan"}, "question_links": self.runtime["question_links"]}
        extensions = {"question_resolutions": [{"question_id": self.a["id"], "disposition": "resolved", "evidence_refs": ["E"], "reason": "guess"}]}
        self.assertTrue(questions.validate_extensions({}, extensions, context))

    def test_source_identity_not_equal_text_controls_deduplication(self):
        same = questions.link(self.runtime, execution_id="E1", field="output/questions/0", owner="user", targets=["A"], blocks=True)
        self.assertEqual(same["id"], self.a["id"])
        self.assertNotEqual(self.a["id"], self.b["id"])
        self.assertNotIn("text", self.a)

    def test_retry_bypasses_only_the_question_for_its_held_overflow(self):
        other = questions.link(self.runtime, execution_id="E3", field="output/questions/0",
                               owner="user", targets=["A"], blocks=True)
        action = {"id": "AC-1", "role": "research_work", "target": "A",
                  "input_overflow_retry": {"question_id": self.a["id"], "state": "pending"}}
        waits = questions.user_waits(action, self.instance, self.runtime)
        self.assertEqual([row["question_id"] for row in waits], [other["id"]])

        action["input_overflow_retry"]["state"] = "resolved"
        waits = questions.user_waits(action, self.instance, self.runtime)
        self.assertEqual({row["question_id"] for row in waits}, {self.a["id"], other["id"]})

    def test_overflow_question_text_follows_its_artifact_pointer(self):
        class Store:
            def read_many(inner, refs, head):
                return {refs[0]: b'{"resolution_question":{"question":"Choose an authorized larger profile."}}'}
        reader = QuestionEngineMixin()
        reader.store, reader.head, reader.instance = Store(), "H", {"decisions": {}}
        reader.runtime = {"question_links": [{
            "id": "QU-overflow", "origin_execution_id": "EX-overflow",
            "origin_field": "resolution_question/question",
            "source_ref": "runtime/artifacts/BA-overflow/input-overflow.json",
            "owner": "user", "target_ids": ["AC-held"], "unresolved_target_ids": ["AC-held"],
            "blocks": True, "status": "open", "resolution_ref": None}]}
        row = reader._question_view()[0]
        self.assertEqual(row["text"], "Choose an authorized larger profile.")
        self.assertNotIn("source_status", row)

    def test_review_questions_include_pending_research_without_a_result(self):
        # A limit closure can publish while another slot's fixed question is still pending.
        owner = QuestionEngineMixin()
        owner.runtime = {"question_links": []}
        cycle = {"id": "RC-closed", "knowledge_id": "KN-reviewed", "followup": [], "research": {
            "EX-a:first": {"status": "pending", "question": "Is the binder fixed?", "result": None},
            "EX-b:second": {"status": "unresolved", "question": "Which domain?",
                            "result": {"output": {"questions": ["The domain remains open"]}}}}}
        owner._record_review_questions(cycle, "EX-closing")
        self.assertEqual([row["origin_field"] for row in owner.runtime["question_links"]], [
            "research/EX-a:first/question", "research/EX-b:second/question",
            "research/EX-b:second/result/output/questions/0"])
        self.assertTrue(all(row["source_id"] == "RC-closed" for row in owner.runtime["question_links"]))


class RepetitionQuestionTests(unittest.TestCase):
    def host(self):
        from copy import deepcopy
        from do_math import revisions
        from do_math.governance import preserve_source
        host = QuestionEngineMixin()
        host.instance = {'id': 'I', 'config': {'selection_failure_limit': 1},
            'governance_sources': {'S': preserve_source('S', 'Authorize the exact continuation.', origin='user')},
            'decisions': {}}
        action = {'id': 'AC-held', 'role': 'research_plan',
                  'repetition_bases': {'selection_failure': 'population'}}
        host.runtime = {'tasks': {}, 'history': [], 'queue': [action], 'executions': {
            'EX-first': {'id': 'EX-first', 'role': 'research_plan', 'status': 'ended',
                         'action': deepcopy(action)}}}
        revisions.record_repetition(host.instance, host.runtime, lineage='selection_failure',
            lineage_id='population', event_ref='EX-first', outcome='rejected', owner='ai',
            reason='The returned plan omitted a candidate.')
        return host, action

    def test_limit_question_reads_preserved_history_after_roundtrip_and_append(self):
        import json
        from do_math import revisions
        from do_math.record_schemas import RECORDS
        from jsonschema import Draft202012Validator
        host, action = self.host()
        original = revisions.repetition_hold(host.runtime, 'selection_failure', 'population')
        host.runtime = json.loads(json.dumps(host.runtime))
        host.runtime['history'].append({'kind': 'unrelated_later_event'})
        row = host._question_view()[0]
        self.assertEqual(row['text'], original['question'])
        self.assertIn('selection_failure/population', row['text'])
        self.assertIn('1/1', row['text'])
        self.assertNotIn('source_status', row)
        self.assertEqual(host._user_questions(), [original['question']])
        Draft202012Validator(RECORDS['question_links']).validate(host.runtime['question_links'][0])
        self.assertTrue(revisions.action_repetition_waits(host.instance, host.runtime, action))

    def test_scoped_continuation_resolves_only_the_current_hold_question(self):
        from copy import deepcopy
        from do_math import revisions
        host, action = self.host()
        first = host.runtime['question_links'][0]
        questions.link(host.runtime, execution_id='EX-other', field='error', owner='user',
                       targets=['I'], blocks=False)
        host.runtime['executions']['EX-other'] = {'id': 'EX-other', 'error': 'A separate choice remains.'}
        change = {'kind': 'repetition_continue', 'lineage': 'selection_failure',
            'lineage_id': 'population', 'hold_event_ref': 'EX-first',
            'allowed_action': revisions.action_scope(action), 'reason': 'Continue the exact held plan.'}
        decision = {'id': 'DC-continue', 'actor': 'user', 'source_ref': 'S', 'change': change}
        host.instance['decisions'][decision['id']] = decision
        revisions.continue_repetition(host.instance, host.runtime, change, decision)
        self.assertEqual(first['status'], 'resolved')
        self.assertEqual(first['resolution_ref'], decision['id'])
        self.assertEqual(host._user_questions(), ['A separate choice remains.'])
        self.assertFalse(revisions.action_repetition_waits(host.instance, host.runtime, action))
        host.runtime['executions']['EX-second'] = {'id': 'EX-second', 'role': 'research_plan',
            'status': 'ended', 'action': deepcopy(action)}
        revisions.record_repetition(host.instance, host.runtime, lineage='selection_failure',
            lineage_id='population', event_ref='EX-second', outcome='rejected', owner='ai',
            reason='The next returned plan still omitted a candidate.')
        current = host.runtime['question_links'][-1]
        self.assertNotEqual(first['origin_field'], current['origin_field'])
        self.assertEqual(current['status'], 'open')
        self.assertIn('EX-second', host._question_view()[-1]['text'])
        self.assertEqual(len(host._user_questions()), 2)


class QuestionRouteWireTests(unittest.TestCase):
    def test_submission_route_controls_only_its_affected_user_wait(self):
        from jsonschema import Draft202012Validator
        from do_math.submission import extension_schema
        validator = Draft202012Validator(extension_schema({'role': 'research_work'}))
        for blocking in (None, False, True):
            with self.subTest(blocking=blocking):
                route = {'question_index': 0, 'owner': 'user', 'target_ids': ['A'],
                         'reason': 'The answer determines the next action on A.'}
                if blocking is not None:
                    route['blocks'] = blocking
                extensions = {'question_routes': [route]}
                validator.validate(extensions)
                owner = QuestionEngineMixin()
                owner.instance = {'id': 'I', 'decisions': {}}
                owner.runtime = {'tasks': {'A': {'id': 'A'}, 'B': {'id': 'B'}},
                    'question_links': [], 'executions': {'EX-route': {
                        'artifact_bundle': 'BA-route', 'extensions': extensions}}}
                output = {'questions': ['Which action on A is authorized?']}
                context = {'instance_id': 'I', 'action': {'role': 'research_work'},
                           'tasks': list(owner.runtime['tasks'].values())}
                self.assertEqual(questions.validate_extensions(output, extensions, context), [])
                owner._record_output_questions({'role': 'research_work', 'target': 'A'}, output, 'EX-route')
                linked = owner.runtime['question_links'][0]
                self.assertEqual(linked['blocks'], blocking is True)
                waits = lambda target: questions.user_waits(
                    {'role': 'research_work', 'target': target}, owner.instance, owner.runtime)
                self.assertEqual(bool(waits('A')), blocking is True)
                self.assertEqual(waits('B'), [])
                questions.resolve_user(owner.runtime, [linked['id']], resolution_ref='DC-answer', affected_ids=['A'])
                self.assertEqual(waits('A'), [])
        route['blocks'] = 'true'
        self.assertTrue(list(validator.iter_errors({'question_routes': [route]})))
if __name__ == "__main__":
    unittest.main()
